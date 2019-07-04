import os, traceback, sys, json, base64
from flask import Flask, jsonify, request, Response, send_from_directory
import apis

app = Flask(__name__)

# add skiturer routes
app.register_blueprint(apis.skiturer, url_prefix='/skiturer-norge')
app.register_blueprint(apis.hvor_mye_warmere, url_prefix='/hvor-mye-warmere')

@app.route('/',methods=['GET'])
def home():
    return('<h1>An API Service</h1>')

if __name__=='__main__':
    app.run(port=8000,debug=True)
