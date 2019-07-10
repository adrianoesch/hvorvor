import os, json, requests
from requests.auth import HTTPBasicAuth
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from github import Github
from geopy.distance import distance

hvor_mye_warmere = Blueprint('hvor-mye-warmere', __name__)
CORS(hvor_mye_warmere)

sources = json.load(open('apis/data/coords.json','r'))

def sortStations(coords,year):
    searchSources = [(i['id'],i['geometry']['coordinates']) for i in sources ]

    i=1
    for i in range(0,100,10):
        requestSources = ','.join([j[0] for j in searchSources[i:i+10]])
        r = requests.get('https://frost.met.no/observations/availableTimeSeries/v0.jsonld',
            params={'sources':requestSources},
            auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
        )
        timeSeries = r.json()['data']
        uri = [i for i in timeSeries if 'air_temperature' in i['elementId']][0]['uri']
    r = requests.get(uri.replace('//auth',''),
        auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
    )
    r.json()['data']



@hvor_mye_warmere.route('/',methods=['GET'])
def route():
    lat = int(request.args.get('lat'))
    lng = int(request.args.get('lng'))
    year = int(request.args.get('year'))
    source_dists = [ ( i[0], distance((lat,lng), i[1]).km ) for i in searchSources if year > int(i['validFrom'][:4])]
    source_dists.sort(key = lambda i :i[1])
    source_id = source_dists[0][0]
    r = requests.get('https://frost.met.no/observations/availableTimeSeries/v0.jsonld',
            params={
                'sources':source_id,
                'elements':'best_estimate_mean(air_temperature_anomaly P1M 1961_1990,best_estimate_mean(air_temperature_anomaly P1Y 1961_1990'
            },
            auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
        )
    print(r.status_code)
    print(r.json())
    return jsonify({'success':'True'})



# d = json.load(open('public/assets/sources_p1m.json','r'))
# ids = ','.join([i['sourceId'].split(':')[0] for i in d['data']])
# r = requests.get('https://frost.met.no/sources/v0.jsonld?ids='+ids,auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET']))
# s = r.json()['data']
#
# ids = ','.join([i['sourceId'].split(':')[0] for i in d['data']][100:200])
# r = requests.get('https://frost.met.no/sources/v0.jsonld?ids='+ids,auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET']))
# s.extend(r.json()['data'])
#
# ids = ','.join([i['sourceId'].split(':')[0] for i in d['data']][200:])
# r = requests.get('https://frost.met.no/sources/v0.jsonld?ids='+ids,auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET']))
# s.extend(r.json()['data'])
#
# d_ids = [j['sourceId'].split(':')[0] for j in d['data']]
# s_ids = [i['id'] for i in s]
#
# s2={}
# for i in d['data']:
#     if not i['sourceId'].split(':')[0] in s_ids:
#         print(i['sourceId'])
#


# json.dump(s,open('public/assets/coords.json','w'))
#
# # i=d['data'][12]
# for i in d['data']:
#     r = requests.get('https://frost.met.no/sources=',
#         params={'sources':requestSources},
#         auth=HTTPBasicAuth(os.environ['FROST_KEY'],os.environ['FROST_SECRET'])
#     )
#     i['sourceId']
#
#



# issues:
# - missing source coordinates
