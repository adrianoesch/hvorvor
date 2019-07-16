import dateutil.parser
from datetime import datetime
import os, json, requests
from requests.auth import HTTPBasicAuth
x=dateutil.parser.parse('9999-12-31T23:59:59Z')

os.chdir('/Users/adroesch/Desktop/private/hvorvor')
d = json.load(open('apis/data/sources_air_p1y.json','r'))
air_sources = {}
for i in d['data']:
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
request_ids = ','.join([k.split(':')[0] for k,v in air_sources.items()])
r = requests.get('https://frost.met.no/sources/v0.jsonld',
        params={'ids':request_ids},
        auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
)
d = r.json()['data']

air_sources = {k.split(':')[0]:v for k,v in air_sources.items()}
for i in d:
    for k,v in i.items():
        if not k in air_sources[i['id']].keys():
            air_sources[i['id']][k]=v
json.dump(air_sources,open('apis/data/sources_air_p1y_clean.json','w'))
