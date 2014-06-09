# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'


class AbstractInterface(object):
    @classmethod
    def install_timerush_object(cls, t):
        cls.timerush = t

    def register(self, callback_cmd, callback_data, seconds):
        return self.timerush.register(callback_cmd, callback_data, seconds)

    def unregister(self, key):
        return self.timerush.unregister(key)

    def notify(self, callback_cmd, callback_data):
        raise NotImplementedError()

    def run(self, *args, **kwargs):
        raise NotImplementedError()
