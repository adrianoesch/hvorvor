import dateutil.parser
from datetime import datetime
import os, json, requests
from requests.auth import HTTPBasicAuth

x=dateutil.parser.parse('9999-12-31T23:59:59Z')

os.chdir('/Users/adroesch/Desktop/private/hvorvor')
r = requests.get('https://frost.met.no/observations/availableTimeSeries/v0.jsonld',
        params={
            'elements':'mean(air_temperature P1Y)'
        },
        auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
)
d = r.json()['data']

air_sources = {}
for i in d:
    if not i['sourceId'] in air_sources:
        air_sources[i['sourceId']]={
            'from':i.get('validFrom'),
            'to':i.get('validTo','9999-12-31T23:59:59Z')
        }
    else:
        air_sources[i['sourceId']]={
            'from': min(
                dateutil.parser.parse(i.get('validFrom')),
                dateutil.parser.parse(air_sources[i['sourceId']]['from'])
            ).isoformat().replace("+00:00", "Z"),
            'to': max(
                dateutil.parser.parse(i.get('validTo','9999-12-31T23:59:59Z')),
                dateutil.parser.parse(air_sources[i['sourceId']]['to'])
            ).isoformat().replace("+00:00", "Z"),
        }

air_sources = {k:v for k,v in air_sources.items() if v['to'][:4]=='9999'}

air_sources.items()
request_ids = ','.join([k.split(':')[0] for k,v in air_sources.items()][100:])
r = requests.get('https://frost.met.no/sources/v0.jsonld',
        params={'ids':request_ids},
        auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
)
# d = d+r.json()['data']

air_sources = {k.split(':')[0]:v for k,v in air_sources.items()}
for i in d:
    for k,v in i.items():
        if not k in air_sources[i['id']].keys():
            air_sources[i['id']][k]=v
json.dump(air_sources,open('projects/hvor_mye_warmere/data/sources_mean_air_p1y_clean.json','w'))

# max temps
r = requests.get('https://frost.met.no/observations/availableTimeSeries/v0.jsonld',
        params={'elements':'max(air_temperature P1D)'},
        auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
)
os.chdir('/Users/adroesch/Desktop/private/hvorvor/projects/hvor_mye_warmere/')
json.dump(r.json()['data'],open('data/archive/sources_maxtemp_p1d.json','w'))

# from collections import Counter
# c=Counter([i['from'][:4] for i in air_sources.values()])
# c=[(k,v) for k,v in c.items()]
# c.sort(key=lambda i: i[0])
