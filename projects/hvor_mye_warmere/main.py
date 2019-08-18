import os, json, requests
from flask_httpauth import HTTPBasicAuth as basic_auth
from datetime import datetime
from requests.auth import HTTPBasicAuth
from flask import Blueprint, jsonify, request, send_from_directory, Response, send_file
from flask_cors import CORS
from github import Github
from geopy.distance import distance
from .utils.frost import Frost

# global settings
n_rolling_avg_years=10
hot_days_threshold=25
airTemp_sources_path = 'projects/hvor_mye_warmere/data/sources_air_p1y_clean.json'
hotDays_sources_path = 'projects/hvor_mye_warmere/data/sources_maxtemp_p1d_clean.json'
rain_sources_path = 'projects/hvor_mye_warmere/data/sources_maxtemp_p1d_clean.json'

hvor_mye_warmere = Blueprint('hvor-mye-warmere', __name__, static_folder='static')
airTempSources = json.load(open(airTemp_sources_path,'r'))
hotDaysSources = json.load(open(hotDays_sources_path,'r'))
rainSources = json.load(open(rain_sources_path,'r'))
sourcesDic={
    'airTemp': airTempSources,
    'hotDays': hotDaysSources,
    'rain': rainSources
}
cacheDir = 'projects/hvor_mye_warmere/data/cache/' if not 'apis' in os.getcwd() else 'data/cache/'


frost = Frost(cacheDir,n_rolling_avg_years,hot_days_threshold)
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
    airTempSource = getNearestSource(lat,lng,year,'airTemp')
    hotDaysSource = getNearestSource(lat,lng,year,'hotDays')
    rainSource = getNearestSource(lat,lng,year,'rain')
    time_series = frost.getTimeSeries(airTempSource['id'],hotDaysSource['id'],rainSource['id'],year)
    return jsonify({
            'success':'True',
            'request': {
                'name':name,
                'coords':{
                    'lat':lat,
                    'lng':lng,
                },
                'year':year
            },
            'airTempSource' : airTempSource,
            'hotDaysSource' : hotDaysSource,
            'rainSource': rainSource,
            'timeSeries': time_series,
            'n_rolling_avg_years': n_rolling_avg_years,
            'hot_days_threshold': hot_days_threshold
        })

def getNearestSource(lat,lng,year,metric):
    sources = sourcesDic[metric]
    sources_time_filtered = [
        (k, (v['geometry']['coordinates'][1], v['geometry']['coordinates'][0]))
        for k,v in sources.items() if year-n_rolling_avg_years >= int(v['from'][:4])
    ]
    sources_dists = [ ( i[0], i[1], distance((lat,lng),i[1]).km ) for i in sources_time_filtered]
    sources_dists.sort(key = lambda i :i[2])
    nearest_source = {
        'id' : sources_dists[0][0],
        'coords' : {
            'lat':sources_dists[0][1][0],
            'lng':sources_dists[0][1][1]
            },
        'distance_in_km' : sources_dists[0][2]
    }
    return nearest_source
