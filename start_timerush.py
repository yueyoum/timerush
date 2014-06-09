# -*- coding: utf-8 -*-

__author__ = 'Wang Chao'
__date__ = '14-6-7'


"""
Protocol

    Start a new timer
        requests data format:
        {
            'callback_cmd':     callback_cmd,    # your system callback location. url for http, ip:port for socket
            'callback_data':    callback_data,   # a json serialized object. TimeRush will notify your system with this data
            'seconds':          seconds,         # TimeRush will notify you after this seconds
        }

        return:
        {
            'ret': integer,         # 0 means no error.
            'msg': string,          # only exist when ret != 0
            'data': {
                'key': string,      # only exist when ret == 0
            }
        }

        if ret == 0, you will got a key. you can cancel a timer with this key.

    Cancel a timer
        request data format:
        {
            'key': key
        }

        return:
        {
            'ret': integer,     # 0 means no error
            'msg': string,      # only exist when ret != 0
            'data': {
                'ttl': integer, # seconds remaining of this timer
            }
        }

    Notify
        When a timer finish, TimeRush will notify your system with the `callback_data`

        your system return:
        {
            'ret': 0,
        }



Default Backend
    - timerush.backend.redis.RedisBackend


Default Interface
    - timerush.interface.http.HTTPInterface

        HTTP interface has two uri for collect requests:

        request only support POST method,
        request data must be a JSON serialized object, and attach in request body directly. not a key value format.
        timerush will return json object

        -   /register/
            start a new timer


        -   /unregister/
            cancel a timer



When TimeRush Got a new request,
It will notify your system after [seconds], to [callback_cmd], with [callback_data].

This three variables are actually you have sent to TimeRush.

When your system receive the notify from TimeRush,
your system should return

    {
        'ret': 0
    }

    this means this job is complete.

    OR

    {
        'ret': 0,
        'data': {
            'callback_cmd': callback_cmd,
            'callback_data': callback_data,
            'seconds': seconds
        }
    }

    this like the /register/ request.
    TimeRush will create a new timer with this params.


Example:

    you request register with this data:

    {
        'callback_cmd': 'http://your_system_domain/timerush/',
        'callback_data': {'name': 'a', 'from': 'you', 'time': 60},
        'seconds': 60,
    }

    then you got a key from the request return

    you can cancel this timer by send this data to unregister

    {
        'key': key
    }

    when seconds over, your system will get a notify with the callback_data:
    {'name': 'a', 'from': 'you', 'time': 60}

    if you return

    {
        'ret': 0
    }

    this timer will be complete.

    or you return

    {
        'ret': 0,
        'data': {
            'callback_cmd': 'http://your_system_domain/timerush/',
            'callback_data': {'name': 'a', 'from': 'you', 'time': 80},
            'seconds': 20,
        }
    }

    TimeRush will start a new timer, which after 20 seconds will notify your system again.

    NOTICE the time is 80, because when the second notify arrival your system,
    the time actually passed 80 seconds.

More info see example
"""

import sys
from docopt import docopt
from daemonized import Daemonize
from timerush import TimeRush


USAGE = """
Usage: start_timerush.py [--host=ARG] [--port=ARG] [--db=ARG] [--key=ARG] [--interval=ARG] [--listen-host=ARG] [--listen-port=ARG] [--pem=ARG] [--level=ARG] [-d] [--logpath=ARG]

--host=ARG    Redis Host [default: 127.0.0.1]
--port=ARG    Redis Port [default: 6379]
--db=ARG      Redis DB   [default: 0]
--key=ARG     Redis KEY  [default: _timerush_redis_data_]
--interval=ARG      Backend Check Workers Status Interval [default: 60]
--listen-host=ARG   Interface Listen Host [default: 127.0.0.1]
--listen-port=ARG   Interface Listen Port [default: 8080]
--pem=ARG           Interface Notify Https Pem
--level=ARG         Log Level [default: DEBUG]
-d                  Daemonize [default: False]
--logpath=ARG       Log Path
"""


def main():
    opt = docopt(USAGE)
    print opt
    backend_kwargs = {
        'host': opt['--host'],
        'port': int(opt['--port']),
        'db': int(opt['--db']),
        'data_key': opt['--key'],
        'check_status_interval': int(opt['--interval']),
    }

    interface_kwargs = {
        'listener': (opt['--listen-host'], int(opt['--listen-port'])),
        'pem': opt['--pem']
    }

    log_level = opt['--level']


    daemon = opt['-d']
    if daemon:
        logpath = opt['--logpath']
        if not logpath:
            sys.stderr.write("you enable daemonize, So must set the logpath.\n")
            sys.exit(1)

        if not logpath.startswith('/'):
            sys.stderr.write("logpath must be absolute path.\n")
            sys.exit(2)

        Daemonize(stdout=logpath, stderr=logpath).make_daemon()


    TimeRush(
        interface_kwargs=interface_kwargs,
        backend_kwargs=backend_kwargs,
        log_level=log_level,
    ).run()



if __name__ == '__main__':
    main()
