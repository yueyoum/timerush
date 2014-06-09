# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'

import os
import logging
import json
import traceback
import requests
from bottle import request, Bottle
from gevent.pywsgi import WSGIServer

from timerush.interface import AbstractInterface

logger = logging.getLogger('timerush.interface.http')


class HTTPInterface(AbstractInterface):
    def __init__(self, listener, pem=None):
        self.listener = listener
        self.pem = pem

        if self.pem and not os.path.exists(self.pem):
            raise IOError("PEM file not exists. {0}".format(self.pem))


    def notify(self, callback_cmd, callback_data):
        req_kwargs = {'data': callback_data}

        if self.pem:
            req_kwargs.update({
                'verify': False,
                'cert': self.pem
            })

        req = requests.post(callback_cmd, **req_kwargs)
        if not req.ok:
            logger.error("Notify Failure!")
            return False

        return True


    def run(self):
        app = Bottle()

        @app.post('/register/')
        def _register():
            data = request.body.read()
            logger.info("REGISTER Got Data: {0}".format(data))
            try:
                data = json.loads(data)
                callback_cmd = data['callback_cmd']
                callback_data = data['callback_data']
                seconds = int(data['seconds'])
                assert seconds > 0
            except:
                logger.error("Invalid Data")
                logger.error(traceback.format_exc())
                return {'ret': 1, 'msg': 'Invalid Data'}

            key = self.register(callback_cmd, callback_data, seconds)
            return {
                'ret': 0,
                'data': {
                    'key': key
                }
            }

        @app.post('/unregister/')
        def _unregister():
            data = request.body.read()
            logger.info("UNREGISTER Got Data: {0}".format(data))
            try:
                data = json.loads(data)
                key = data['key']
            except:
                logger.error("UNREGISTER Invalid Data")
                logger.error(traceback.format_exc())
                return {'ret': 1, 'msg': 'Invalid Data'}

            ttl = self.unregister(key)
            return {
                'ret': 0,
                'data': {
                    'ttl': ttl
                }
            }

        server = WSGIServer(self.listener, app)
        server.serve_forever()
