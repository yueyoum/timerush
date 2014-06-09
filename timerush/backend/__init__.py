# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'

import logging
import gevent

logger = logging.getLogger('timerush.backend')

class AbstractBackend(object):
    @classmethod
    def install_timerush_object(cls, t):
        cls.timerush = t

    def __init__(self, check_status_interval=60):
        self.check_status_interval = check_status_interval
        self.workers = {}

        gevent.spawn_later(1, self._check_status)


    def _check_status(self):
        while True:
            logger.debug("Workers amount: {0}".format(len(self.workers)))
            gevent.sleep(self.check_status_interval)


    def start_worker(self, callback_cmd, callback_data, seconds, key):
        worker = TimerWorker(callback_cmd, callback_data, seconds, key)
        worker.link_value(self.notify)
        worker.start()

        self.workers[key] = worker


    def register(self, callback_cmd, callback_data, seconds):
        key = self.add(callback_cmd, callback_data, seconds)
        self.start_worker(callback_cmd, callback_data, seconds, key)
        return key


    def unregister(self, key):
        try:
            glet = self.workers.pop(key)
            glet.kill()
        except KeyError:
            pass

        return self.remove(key)


    def notify(self, glet):
        if not glet.final_finished:
            return

        job = gevent.spawn(self.timerush.notify, glet.callback_cmd, glet.callback_data)
        job.join()
        ok = job.value
        if ok:
            self.unregister(glet.key)


    def add(self, callback_cmd, callback_data, seconds):
        raise NotImplementedError()


    def remove(self, key):
        raise NotImplementedError()


    def run(self, *args, **kwargs):
        raise NotImplementedError()




class TimerWorker(gevent.Greenlet):
    def __init__(self, callback_cmd, callback_data, seconds, key):
        gevent.Greenlet.__init__(self)
        self.callback_cmd = callback_cmd
        self.callback_data = callback_data
        self.seconds = seconds
        self.key = key
        self.final_finished = False

    def _run(self):
        gevent.sleep(self.seconds)
        self.final_finished = True
        logger.info("Worker finish. key: {0}".format(self.key))

