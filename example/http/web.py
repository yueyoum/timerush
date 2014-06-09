# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'

import gevent.monkey
gevent.monkey.patch_all()

import time
import json

from gevent.pywsgi import WSGIServer

from bottle import Bottle, request

app = Bottle()

@app.post('/callback/')
def callback():
    data = request.body.read()
    data = json.loads(data)
    print data
    now = int(time.time())
    text = "time diff = {0}\n".format(now - data['start'] - data['seconds'])

    with open('callback.log', 'a') as f:
        f.write(text)

    return {'ret': 0}
    # return {
    #     'ret': 0,
    #     'data': {
    #             'callback_cmd': 'http://127.0.0.1:8000/callback/',
    #             'callback_data': json.dumps({'nimei': 'jixu'}),
    #             'seconds': 2,
    #         }
    # }


WSGIServer(('127.0.0.1', 8000), app).serve_forever()

