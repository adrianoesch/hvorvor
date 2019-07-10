import os, traceback, sys, json, base64
from flask import Flask, jsonify, request, Response, send_from_directory
from apis.hvor_mye_warmere import hvor_mye_warmere
from apis.skiturer import skiturer

app = Flask(__name__,static_folder='public')

# add skiturer routes
app.register_blueprint(skiturer, url_prefix='/skiturer-norge')
app.register_blueprint(hvor_mye_warmere, url_prefix='/hvor-mye-warmere')

@app.route('/',methods=['GET'])
def home():
    return('<h1>Personal API Service</h1>')

@app.route('/<path:path>',methods=['GET'])
def send(path):
    print(path)
    return send_from_directory('public',path)

if __name__=='__main__':
    app.run(port=8000,debug=True)
