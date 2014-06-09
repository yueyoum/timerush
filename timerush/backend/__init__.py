# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'

import gevent

class AbstractBackend(object):
    @classmethod
    def install_timerush_object(cls, t):
        cls.timerush = t

    def register(self, callback_cmd, callback_data, seconds):
        raise NotImplementedError()

    def unregister(self, key):
        raise NotImplementedError()

    def notify(self, callback_cmd, callback_data, key):
        return self.timerush.notify(callback_cmd, callback_data, key)

    def run(self, *args, **kwargs):
        raise NotImplementedError()

