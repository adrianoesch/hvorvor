import os, json, requests
from flask_httpauth import HTTPBasicAuth as basic_auth
from datetime import datetime
from requests.auth import HTTPBasicAuth
from flask import Blueprint, jsonify, request, send_from_directory, Response, send_file
from flask_cors import CORS
from github import Github
from geopy.distance import distance
from .utils.frost import Frost

hvor_mye_warmere = Blueprint('hvor-mye-warmere', __name__, static_folder='static')
sources = json.load(open('projects/hvor_mye_warmere/data/sources_air_p1y_clean.json','r'))
sources = {k:v for k,v in sources.items() if 'geometry' in v}
cacheFile = 'projects/hvor_mye_warmere/data/frost_cache.json' if not 'apis' in os.getcwd() else 'data/frost_cache.json'
n_rolling_avg_years=10
frost = Frost(cacheFile,n_rolling_avg_years=n_rolling_avg_years)
auth = basic_auth()

@auth.verify_password
def verify_password(username, password):
    user_check = username=='hvor mye?'
    pw_check = password=='for mye!'
    return user_check  and pw_check

@hvor_mye_warmere.route('/',methods=['GET'])
@auth.login_required
def index():
    return send_from_directory(hvor_mye_warmere.static_folder,'index.html')

@hvor_mye_warmere.route('/<path:path>',methods=['GET'])
@auth.login_required
def path(path):
    return send_from_directory(hvor_mye_warmere.static_folder,path)

@hvor_mye_warmere.route('/update/',methods=['GET'])
def update():
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    year = int(request.args.get('year'))
    name = request.args.get('name')
    sources_time_filtered = [(k,(v['geometry']['coordinates'][1],v['geometry']['coordinates'][0])) for k,v in sources.items() if year-n_rolling_avg_years >= int(v['from'][:4])]
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
            'location_name':name,
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
            'annual_rolling': time_series['annual_rolling'],
            'n_rolling_avg_years':n_rolling_avg_years
        })
