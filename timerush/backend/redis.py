from __future__ import absolute_import

# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'

import logging
import uuid
import json
import redis
import arrow

from timerush.backend import AbstractBackend


logger = logging.getLogger('timerush.backend.redis')


def get_ttl(seconds, start, now=None):
    if not now:
        now = arrow.utcnow().timestamp

    ttl = seconds - (now - start)
    return ttl if ttl > 0 else 0



class RedisBackend(AbstractBackend):
    def __init__(self, host, port, db=0, data_key='_timerush_redis_data_', **kwargs):
        self.r = redis.Redis(host=host, port=port, db=db)
        self.data_key = data_key
        super(RedisBackend, self).__init__(**kwargs)


    def run(self):
        self.pre_load()

    def pre_load(self):
        data = self.r.hgetall(self.data_key)

        now = arrow.utcnow().timestamp
        for _key, _data in data.iteritems():
            _data = json.loads(_data)
            ttl = get_ttl(_data['seconds'], _data['start'], now=now)

            self.start_worker(_data['cmd'], _data['data'], ttl, key=_key)


    def add(self, callback_cmd, callback_data, seconds):
        key = str(uuid.uuid4())
        start = arrow.utcnow().timestamp

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
        ttl = get_ttl(data['seconds'], data['start'])

        self.r.hdel(self.data_key, key)
        return ttl

