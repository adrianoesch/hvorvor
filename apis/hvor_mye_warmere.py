import os, json, requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from github import Github
from geopy.distance import distance
from .utils.frost import Frost

hvor_mye_warmere = Blueprint('hvor-mye-warmere', __name__)

# os.chdir('/Users/adroesch/Desktop/private/hvorvor/apis')
sources = json.load(open('apis/data/sources_air_p1y_clean.json','r'))
sources = {k:v for k,v in sources.items() if 'geometry' in v}
cacheFile = 'apis/data/frost_cache.json' if not 'apis' in os.getcwd() else 'data/frost_cache.json'
frost = Frost(cacheFile)

@hvor_mye_warmere.route('/',methods=['GET'])
def route():
    # try:
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    year = int(request.args.get('year'))
    sources_time_filtered = [(k,(v['geometry']['coordinates'][1],v['geometry']['coordinates'][0])) for k,v in sources.items() if year-5 >= int(v['from'][:4])]
    sources_dists = [ ( i[0], i[1], distance((lat,lng),i[1]).km ) for i in sources_time_filtered]
    sources_dists.sort(key = lambda i :i[2])
    nearest_source = {
        'id' : sources_dists[0][0],
        'coords' : sources_dists[0][1],
        'distance' : sources_dists[0][2]
    }
    time_series = frost.getTimeSeries(nearest_source['id'],year)
    difference = time_series['annual_rolling'][-1]['value']-time_series['annual_rolling'][0]['value']
    return jsonify({
            'success':'True',
            'request_coords': {
                'lat':lat,
                'lng':lng
            },
            'source_coords':{
                'lat':nearest_source['coords'][0],
                'lng':nearest_source['coords'][1]
            },
            'source_id':nearest_source['id'],
            'distance_in_km':nearest_source['distance'],
            'difference' : difference,
            'annual': time_series['annual'],
            'annual_rolling': time_series['annual_rolling']
        })
    # except:
    #     return jsonify({'success':'False'})
