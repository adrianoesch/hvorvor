import json, os, requests
from datetime import datetime
import pandas as pd
from requests.auth import HTTPBasicAuth


class Frost:
    def __init__(self,cacheFile):
        self.cacheFile = cacheFile
        self.cache = json.load(open(cacheFile,'r')) if os.path.isfile(cacheFile) else {}

    def cacheWrapper(self,sourceId,timeResolution):
        if sourceId in self.cache.keys() and timeResolution in self.cache[sourceId].keys():
            return self.cache[sourceId][timeResolution]
        else:
            r = requests.get('https://frost.met.no/observations/v0.jsonld',
                    params={
                        'sources':sourceId,
                        'elements':'best_estimate_mean(air_temperature P1Y)' if timeResolution=='P1Y' else 'max(air_temperature P1D)',
                        'referencetime':'1900-01-01T00:00:00Z/9999-01-01T00:00:00Z'
                    },
                    auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
            )
            if r.status_code==200:
                if not sourceId in self.cache.keys():
                    self.cache[sourceId] = {timeResolution: r.json()['data']}
                else:
                    self.cache[sourceId][timeResolution] = r.json()['data']
                with open(self.cacheFile,'w') as f:
                    json.dump(self.cache,f)
                return r.json()['data']
            else:
                return None

    def getData(self,id,timeResolution):
        data = self.cacheWrapper(id,timeResolution)
        return [{'referenceTime':i['referenceTime'],'value':i['observations'][0]['value']} for i in data] if data else None

    def getAnnualTimeSeries(self,id,year):
        annual_series = self.getData(id,'P1Y')
        time_filtered_annual_series = [i for i in annual_series if int(i['referenceTime'][:4])>=year]
        return time_filtered_annual_series

    def getAnnualRollingTimeSeries(self,id,year):
        annual_series = self.getData(id,'P1Y')
        rolling_values = pd.Series([i['value'] for i in annual_series]).rolling(5).mean()
        time_filtered_rolling_series = [{
                'referenceTime' : i['referenceTime'],
                'value':j
            } for i,j in zip(annual_series,rolling_values.values) if int(i['referenceTime'][:4])>=year]
        return time_filtered_rolling_series

    def getDaysAbove25C(self,id,year):
        monthly_series = self.getData(id,'P1D')
        time_filtered_monthly_series = [i for i in monthly_series if int(i['referenceTime'][:4])>=year] if monthly_series else None
        return time_filtered_monthly_series

    def getTimeSeries(self,id,year):
        annual_rolling = self.getAnnualRollingTimeSeries(id,year)
        r = {
            'annual': self.getAnnualTimeSeries(id,year),
            'annual_rolling': annual_rolling
            # 'days_above_25c': self.getDaysAbove25C(id,year)
        }
        return r
