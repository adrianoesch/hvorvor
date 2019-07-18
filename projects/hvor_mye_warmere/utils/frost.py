import json, os, requests
from datetime import datetime
import pandas as pd
from requests.auth import HTTPBasicAuth


class Frost:
    def __init__(self,cacheFile,n_rolling_avg_years=10,hot_days_threshold=25):
        self.cacheFile = cacheFile
        self.n_rolling_avg_years = n_rolling_avg_years
        self.hot_days_threshold = hot_days_threshold
        self.cache = json.load(open(cacheFile,'r')) if os.path.isfile(cacheFile) else {}

    def cacheWrapper(self,sourceId,metric):
        if sourceId in self.cache.keys() and metric in self.cache[sourceId].keys():
            return self.cache[sourceId][metric]
        else:
            params={
                'sources':sourceId,
                'elements':'best_estimate_mean(air_temperature P1Y)' if metric == 'P1Y' else 'max(air_temperature P1D)',
                'referencetime':'1900-01-01T00:00:00Z/2019-01-01T00:00:00Z'
            }
            if metric == 'P1D':
                params['timeoffsets']='PT18H'
            r = requests.get('https://frost.met.no/observations/v0.jsonld', params,
                    auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
            )
            if r.status_code==200:
                data = r.json()['data']
                data = [{'referenceTime':i['referenceTime'],'value':i['observations'][0]['value']} for i in data] if data else None
                self.saveInCache(sourceId,metric,data)
                return data
            else:
                return None

    def saveInCache(self,sourceId,metric,data):
        if not sourceId in self.cache.keys():
            self.cache[sourceId] = {metric: data}
        else:
            self.cache[sourceId][metric] = data
        with open(self.cacheFile,'w') as f:
            json.dump(self.cache,f)
        return 'Success'

    def transformRollingAvg(self,series,year):
        rolling_values = pd.Series([i['value'] for i in series]).rolling(self.n_rolling_avg_years).mean()
        time_filtered_rolling_series = [{
                'year' : i['year'],
                'value': j
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
        annual_series = self.getAnnualAvgAirTempTimeSeries(id,year-self.n_rolling_avg_years)
        rolling_series  = self.transformRollingAvg(annual_series,year)
        return rolling_series

    def getAnnualHotDaysTimeSeries(self,id,year):
        annual_series = self.cacheWrapper(id,'P1D')
        time_filtered_annual_series = [{
                'year':  int(i['referenceTime'][:4]),
                'value': 1  if i['value']>self.hot_days_threshold else 0
            } for i in annual_series if int(i['referenceTime'][:4])>=year
        ]
        grouped_series = pd.DataFrame(time_filtered_annual_series).groupby('year').sum().reset_index().to_dict(orient='records')
        return grouped_series

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
        }
        return r
