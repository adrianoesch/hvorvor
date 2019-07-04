import os, json
from flask import Blueprint, jsonify, request
from flask_cors import CORS
from github import Github

skiturer = Blueprint('skiturer', __name__)
CORS(skiturer)

@skiturer.route('/route/create',methods=['POST'])
def routeHandler():
    g = Github(os.environ['GH_USER'],os.environ['GH_PWD'])
    repo = g.get_repo("skiturer-norge/skiturer-norge.github.io")
    post = json.loads(request.get_data())
    fileSaveName = ''.join([i if i.isalnum() else '_' for i in post['name']])
    fileName = fileSaveName+'-'+os.urandom(3).hex()+'.gpx'
    path = os.path.join('ruter/user/',fileName)
    repo.create_file(path,'new route (web)',post['gpx'])
    routes = repo.get_contents('ruter/user_onload.txt')
    new_content = base64.b64decode(routes.content).decode('utf8')+fileName+'\n'
    repo.update_file(routes.path,'new route to list (web)',new_content,routes.sha)
    return jsonify({'success':'True'})
