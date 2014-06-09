# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'


class AbstractInterface(object):
    @classmethod
    def install_timerush_object(cls, t):
        cls.timerush = t

    def register(self, callback_cmd, callback_data, seconds, key=None):
        return self.timerush.register(callback_cmd, callback_data, seconds, key=key)

    def unregister(self, key):
        self.timerush.unregister(key)

    def notify(self, *args, **kwargs):
        raise NotImplementedError()

    def run(self, *args, **kwargs):
        raise NotImplementedError()
