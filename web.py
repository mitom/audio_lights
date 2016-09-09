from flask import Flask, render_template, Response, request
from multiprocessing import Process, Manager
import json
import config

app = Flask(__name__)


manager = config.manager


server = Process(target=app.run)

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/config", methods = ['GET'])
def get_config():
    js = json.dumps(config.config.copy())

    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route("/config", methods = ['POST'])
def set_config():
    data = request.get_json(force=True)

    for key in data:
        config.config[key] = data[key]

    config.dump()
    resp = Response(status=204)
    return resp

@app.route("/reset_config", methods = ['POST'])
def reset_config():
    config.set_default()
    js = json.dumps(config.config.copy())
    config.dump()

    resp = Response(js, status=200, mimetype='application/json')
    return resp

def start():
    config.load()
    server.start()

def stop():
    print "terminating web..."
    server.terminate()
    server.join()