import json, os, requests
from datetime import datetime
import pandas as pd
from requests.auth import HTTPBasicAuth


class Frost:
    def __init__(self,cacheDir,n_rolling_avg_years=10,hot_days_threshold=25):
        self.cacheDir = cacheDir
        self.n_rolling_avg_years = n_rolling_avg_years
        self.hot_days_threshold = hot_days_threshold
        self.fullMetricsMap = {
            'P1Y':'best_estimate_mean(air_temperature P1Y)',
            'P1Ymean':'mean(air_temperature P1Y)',
            'P1D': 'max(air_temperature P1D)',
            'P1Ymax': 'max(air_temperature P1Y)'
        }

    def cacheWrapper(self,sourceId,metric,force=False):
        cacheFiles = [i.split('.')[0] for i in os.listdir(self.cacheDir) if i.split('.')[1]=='json']
        sourceCacheFiles = [i for i in cacheFiles if i.split('_')[0]==sourceId and i.split('_')[1]==metric]
        if len(sourceCacheFiles)>0 and force==False:
            with open(os.path.join(self.cacheDir,sourceCacheFiles[0]+'.json'),'r') as f:
                return json.load(f)
        else:
            params={
                'sources':sourceId,
                'elements': self.fullMetricsMap[metric],
                'referencetime':'1900-01-01T00:00:00Z/2019-01-01T00:00:00Z'
            }
            if metric == 'P1D':
                params['timeoffsets']='PT18H'
            r = requests.get('https://frost.met.no/observations/v0.jsonld', params,
                    auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
            )
            if r.status_code==200:
                data = r.json()['data']
                data = [{'referenceTime':i['referenceTime'],'value':i['observations'][0]['value']} for i in data]
                self.saveInCache(sourceId,metric,data)
                return data
            else:
                return None

    def saveInCache(self,sourceId,metric,data):
        cacheFileName = sourceId+'_'+metric+'.json'
        with open(os.path.join(self.cacheDir,cacheFileName),'w') as f:
            json.dump(data,f)
        return 'Success'

    def transformRollingAvg(self,series,year):
        rolling_values = pd.Series([i['value'] for i in series]).rolling(self.n_rolling_avg_years).mean()
        time_filtered_rolling_series = [{
                'year' : i['year'],
                'value': j if not pd.isnull(j) else None
            } for i,j in zip(series,rolling_values.values) if i['year']>=year
        ]
        return time_filtered_rolling_series

    def getAnnualAvgAirTempTimeSeries(self,id,year):
        annual_series = self.cacheWrapper(id,'P1Y')
        time_filtered_annual_series = [{
                'year':  int(i['referenceTime'][:4]),
                'value': i['value']
            } for i in annual_series if int(i['referenceTime'][:4])>=year
        ]
        return time_filtered_annual_series

    def getRollingAvgAirTempTimeSeries(self,id,year):
        annual_series = self.getAnnualAvgAirTempTimeSeries(id,year-self.n_rolling_avg_years-1)
        rolling_series  = self.transformRollingAvg(annual_series,year)
        return rolling_series


    def getAnnualMaxAirTempTimeSeries(self,id,year):
        annual_series = self.cacheWrapper(id,'P1Ymax')
        time_filtered_annual_series = [{
                'year':  int(i['referenceTime'][:4]),
                'value': i['value']
            } for i in annual_series if int(i['referenceTime'][:4])>=year
        ]
        return time_filtered_annual_series

    def getRollingMaxAirTempTimeSeries(self,id,year):
        annual_series = self.getAnnualMaxAirTempTimeSeries(id,year-self.n_rolling_avg_years-1)
        rolling_series  = self.transformRollingAvg(annual_series,year)
        return rolling_series

    def getAnnualHotDaysTimeSeries(self,id,year):
        annual_series = self.cacheWrapper(id,'P1D')
        time_filtered_annual_series = [{
                'year':  int(i['referenceTime'][:4]),
                'value': 1  if i['value']>self.hot_days_threshold else 0
            } for i in annual_series if int(i['referenceTime'][:4])>=year
        ]
        grouped_series = pd.DataFrame(time_filtered_annual_series).groupby('year').sum().reset_index()
        grouped_series = grouped_series.sort_values('year')
        return grouped_series.to_dict(orient='records')

    def getRollingHotDaysTimeSeries(self,id,year):
        annual_series = self.getAnnualHotDaysTimeSeries(id,year-self.n_rolling_avg_years)
        rolling_series  = self.transformRollingAvg(annual_series,year)
        return rolling_series

    def getTimeSeries(self,airTempId,hotDaysId,year):
        r = {
            'annualAirTemp': self.getAnnualAvgAirTempTimeSeries(airTempId,year),
            'rollingAirTemp': self.getRollingAvgAirTempTimeSeries(airTempId,year),
            'annualHotDays': self.getAnnualHotDaysTimeSeries(hotDaysId,year),
            'rollingHotDays': self.getRollingHotDaysTimeSeries(hotDaysId,year),
            'annualMaxAirTemp': self.getAnnualMaxAirTempTimeSeries(hotDaysId,year),
            'rollingMaxAirTemp': self.getRollingMaxAirTempTimeSeries(hotDaysId,year),
        }
        return r
