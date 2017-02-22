from flask import Response, request, jsonify
from api import app

@app.route('/', methods = ['GET'])
def api_hello():
    data = {
        'hello'  : 'world',
        'number' : 3
    }

    resp = jsonify(data)
    resp.status_code = 200
    return resp

