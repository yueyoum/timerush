from __future__ import absolute_import

# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'

import logging
import uuid
import json
import time
import redis

from timerush.backend import AbstractBackend


logger = logging.getLogger('timerush.backend.redis')



class RedisBackend(AbstractBackend):
    def __init__(self, host, port, db=0, data_key='_timerush_redis_data_', **kwargs):
        self.r = redis.Redis(host=host, port=port, db=db)
        self.data_key = data_key
        super(RedisBackend, self).__init__(**kwargs)


    def run(self):
        self.pre_load()

    def pre_load(self):
        data = self.r.hgetall(self.data_key)

        now = int(time.time())
        for _key, _data in data.iteritems():
            _data = json.loads(_data)
            ttl = _data['seconds'] - (now - _data['start'])
            if ttl < 0:
                ttl = 0

            self.start_worker(_data['cmd'], _data['data'], ttl, key=_key)


    def add(self, callback_cmd, callback_data, seconds):
        key = str(uuid.uuid4())
        start = int(time.time())

        data = {
            'cmd': callback_cmd,
            'data': callback_data,
            'start': start,
            'seconds': seconds,
        }

        self.r.hset(self.data_key, key, json.dumps(data))

        logger.info("Add. key: {0}, callback_cmd: {1}, callback_data: {2}, seconds: {3}, start: {4}".format(
            key, callback_cmd, callback_data, seconds, start
        ))
        return key


    def remove(self, key):
        logger.info("Remove. {0}".format(key))

        data = self.r.hget(self.data_key, key)
        if not data:
            return 0

        data = json.loads(data)
        ttl = data['seconds'] - (int(time.time()) - data['start'])
        if ttl < 0:
            ttl = 0

        self.r.hdel(self.data_key, key)
        return ttl

