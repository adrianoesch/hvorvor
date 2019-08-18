import dateutil.parser
from datetime import datetime
import os, json, requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from collections import Counter

airTempSource = json.load(open('projects/hvor_mye_warmere/data/sources_air_p1y_clean.json','r'))
hotDaysSource = json.load(open('projects/hvor_mye_warmere/data/sources_maxtemp_p1d_clean.json','r'))
rainSource = json.load(open('projects/hvor_mye_warmere/data/sources_rain_p1y.json','r'))

#### series ###
sources = rainSource['data']
clean = {}
for i in sources:
    id = i['sourceId']
    if not id in clean:
        clean[id] = { 'from':[], 'to':[]}
    clean[id]['from'].append(datetime.strptime(i['validFrom'][:10],'%Y-%m-%d'))
    if not 'validTo' in i:
        i['validTo'] = '9999-01-01'
    clean[id]['to'].append(datetime.strptime(i['validTo'][:10],'%Y-%m-%d'))
for k,v in clean.items():
    clean[k]['minFrom'] = min(clean[k]['from'])
    clean[k]['maxTo'] = max(clean[k]['to'])
len(clean)

clean = {k:v for k,v in clean.items() if clean[k]['maxFrom']>=datetime(year=2018,month=1,day=1) and k[:2]=='SN'}
clean = {k.split(':')[0]:v for k,v in clean.items()}


for i in range(5):
    ids  = ','.join([k for k in clean.keys()][i*100:i*100+100])
    r = requests.get('https://frost.met.no/sources/v0.jsonld',
            params={
                'ids': ids
            },
            auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
    )
    r = r.json()['data']
    for j in r[1:]:
        clean[j['id']]['geometry']=j['geometry']

clean = {k:v for k,v in clean.items() if 'geometry' in v}
for k,v in clean.items():
    v['from'] = v['minFrom'].strftime('%Y-%m-%d')
    v['to'] = v['maxFrom'].strftime('%Y-%m-%d')
    v.pop('minFrom')
    v.pop('maxFrom')

with open('sources_rain_p1y_clean.json','w') as f:
    json.dump(clean,f)


#### clean ####
[i for i in airTempSource.values() if 'shortName' in i and 'OSLO' in i['name']]
[i['id'] for i in hotDaysSource.values() if 'shortName' in i and 'OSLO' in i['name']]

remove = ["SN52535","SN68860",'SN49490']

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
