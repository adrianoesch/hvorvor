import dateutil.parser
from datetime import datetime
import os, json, requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from collections import Counter

airTempSource = json.load(open('projects/hvor_mye_warmere/data/sources_air_p1y_clean.json','r'))
hotDaysSource = json.load(open('projects/hvor_mye_warmere/data/sources_maxtemp_p1d_clean.json','r'))

[i for i in airTempSource.values() if 'shortName' in i and 'OSLO' in i['name']]
[i['id'] for i in hotDaysSource.values() if 'shortName' in i and 'OSLO' in i['name']]

remove = ["SN52535"]


json.dump({k:v for k,v in airTempSource.items() if not k in remove},open('projects/hvor_mye_warmere/data/sources_air_p1y_clean.json','w'))
json.dump({k:v for k,v in hotDaysSource.items() if not k in remove},open('projects/hvor_mye_warmere/data/sources_maxtemp_p1d_clean.json','w'))


id='SN50540'
hot_temp_threshold=25
hot_days = {}

r = requests.get('https://frost.met.no/observations/v0.jsonld',
        params={
            'elements':'max(air_temperature P1D)',
            'sources':id,
            'referencetime': '1900-01-01T00:00:00/2019-01-01T00:00:00',
            'timeoffsets':'PT18H'
        },
        auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
)

d = r.json()['data']
len(d)
hot_days[id]=[{
    'year': int(i['referenceTime'][:4]),
    'value': i['observations'][0]['value']}
    for i in d
]

data = hot_days[id]
pd.DataFrame(data).groupby('year').sum().reset_index().to_dict(orient='records')


d2 = json.load(open('projects/hvor_mye_warmere/data/frost_cache.json','r'))
d2['SN18700']
