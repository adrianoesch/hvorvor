import os, traceback, sys, json, base64
from flask import Flask, jsonify, request, Response, send_from_directory
from projects.hvor_mye_warmere.main import hvor_mye_warmere
from projects.skiturer import skiturer

app = Flask(__name__,static_folder='public')

# routes
app.register_blueprint(skiturer, url_prefix='/skiturer-norge')
app.register_blueprint(hvor_mye_warmere, url_prefix='/hvor-mye-warmere')

@app.route('/<path:path>',methods=['GET'])
def send(path):
    return send_from_directory('public',path)

if __name__=='__main__':
    app.run(port=8000,debug=True)
