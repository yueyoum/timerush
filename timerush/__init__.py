# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'

import gevent.monkey
gevent.monkey.patch_all()

import logging

from timerush.backend.redis import RedisBackend
from timerush.interface.http import HTTPInterface


LOG_LEVEL_TABLE = {
    'NOTSET': logging.NOTSET,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}



class TimeRush(object):
    def __init__(self, INTERFACE_CLASS=None, BACKEND_CLASS=None, interface_kwargs=None, backend_kwargs=None, log_level='DEBUG'):
        INTERFACE= INTERFACE_CLASS or HTTPInterface
        BACKEND = BACKEND_CLASS or RedisBackend

        INTERFACE.install_timerush_object(self)
        BACKEND.install_timerush_object(self)

        self.INTERFACE = INTERFACE(**interface_kwargs)
        self.BACKEND = BACKEND(**backend_kwargs)

        self.register = self.BACKEND.register
        self.unregister = self.BACKEND.unregister
        self.notify = self.INTERFACE.notify

        self.build_logger(log_level)


    def run(self):
        self.BACKEND.run()
        self.INTERFACE.run()


    def build_logger(self, log_level):
        level = LOG_LEVEL_TABLE[log_level]

        logger = logging.getLogger('timerush')
        logger.setLevel(level)

        fmt = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
        stream_handle = logging.StreamHandler()
        stream_handle.setLevel(level)
        stream_handle.setFormatter(fmt)

        logger.addHandler(stream_handle)

        logger.info("TimeRush Start")

