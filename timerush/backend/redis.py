from __future__ import absolute_import

# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'

import sys
import logging
import uuid
import json
import redis
import gevent

from timerush.backend import AbstractBackend

CHANNEL= '__keyevent@0__:expired'

logger = logging.getLogger('timerush.backend.redis')


class RedisBackend(AbstractBackend):
    def __init__(self, host, port, data_key='_timerush_redis_data_'):
        self.r = redis.Redis(host=host, port=port, db=0)
        self.data_key = data_key
        # self._data = {}


    def run(self):
        self.pre_load()

        job_check = gevent.spawn(self.check)
        job_get = gevent.spawn(self.get_message)

        def _exit(glet):
            glet.unlink(_exit)
            gevent.killall([job_check, job_get])
            logger.error("----ERROR. EXIT----")
            logger.error(glet.exception)
            sys.exit(1)

        job_check.link_exception(_exit)
        job_get.link_exception(_exit)


    def pre_load(self):
        pipe = self.r.pipeline(transaction=False)
        keys = self.r.hkeys(self.data_key)

        logger.info("PreLoad, Got Keys Amount {0}".format(len(keys)))

        for k in keys:
            pipe.ttl(k)

        ttls = pipe.execute()

        for _key, _ttl in zip(keys, ttls):
            if not _ttl:
                self.make_notify(_key)


    def check(self):
        pipe = self.r.pipeline()

        cursor = 0
        while True:
            gevent.sleep(10)

            cursor, data = self.r.hscan(self.data_key, cursor=cursor)
            logger.debug("Check. Got Amount {0}".format(len(data)))
            for k in data.keys():
                pipe.ttl(k)

            pipe.execute()


    def register(self, callback_cmd, callback_data, seconds, key=None):
        if not key:
            key = str(uuid.uuid4())
            key_sign = 'NEW'
        else:
            key_sign = 'OLD'

        data = {
            'cmd': callback_cmd,
            'data': callback_data,
        }

        pipe = self.r.pipeline()
        pipe.hset(self.data_key, key, json.dumps(data))
        pipe.setex(key, 1, seconds)
        pipe.execute()

        # self._data[key] = data

        logger.info("Register. key[{0}]: {1}, callback_cmd: {2}, callback_data: {3}, seconds: {4}".format(
            key_sign, key, callback_cmd, callback_data, seconds
        ))
        return key


    def unregister(self, key):
        pipe = self.r.pipeline(transaction=False)
        pipe.hdel(self.data_key, key)
        pipe.delete(key)
        pipe.execute()

        # try:
        #     self._data.pop(key)
        # except KeyError:
        #     pass

        logger.info("Unregister. {0}".format(key))



    def get_message(self):
        p = self.r.pubsub()
        p.subscribe(CHANNEL)
        init_msg = p.get_message()
        if not init_msg or init_msg['type'] != 'subscribe':
            raise Exception("Subscribe Failue. msg: {0}".format(init_msg))

        logger.info("Subscribe Succeed. Channel: {0}".format(CHANNEL))
        while True:
            msg = p.get_message()
            if msg:
                logger.info("Got Message {0}".format(msg))
                key = msg['data']
                self.make_notify(key)

            gevent.sleep(0.01)


    def make_notify(self, key):
        # try:
        #     data = self._data[key]
        # except KeyError:
        data = self.r.hget(self.data_key, key)
        if not data:
            return

        data = json.loads(data)

        callback_cmd = data['cmd']
        callback_data = data['data']

        def _clean(glet):
            if not glet.value:
                return

            self.r.hdel(self.data_key, key)
            # try:
            #     self._data.pop(key)
            # except KeyError:
            #     pass

        job_notify = gevent.spawn(self.notify, callback_cmd, callback_data, key)
        job_notify.link_value(_clean)
