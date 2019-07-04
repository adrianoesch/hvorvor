import os, json, requests
from requests.auth import HTTPBasicAuth
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from github import Github
from geopy.distance import distance

hvor_mye_warmere = Blueprint('hvor-mye-warmere', __name__)
CORS(hvor_mye_warmere)

sources = json.load(open('sources_no.json','r'))
sources = [i for i in sources if 'geometry' in i]
sources = [i for i in sources if 'coordinates' in i['geometry']]

coords = (7.1046013,61.27102)
year = 1980

def sortStations(coords,year):
    searchSources = [(i['id'],i['geometry']['coordinates']) for i in sources if year > int(i['validFrom'][:4])]
    searchSources = [ ( i[0], distance(coords, i[1]).km ) for i in searchSources]
    searchSources.sort(key = lambda i :i[1])
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



@hvor_mye_warmere.route('/find-station',methods=['GET'])
def findStation():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    year = request.args.get('year')

    return jsonify({'success':'True'})
