import sys
import time
import json
import random
import requests

TIMERUSH_URL = 'http://127.0.0.1:8080'
CALLBACK_URL = 'http://127.0.0.1:8000/callback/'

def register(seconds):
    callback_data = {
            'start': int(time.time()),
            'seconds': seconds,
            }

    data = {
        'callback_cmd': CALLBACK_URL,
        'callback_data': json.dumps(callback_data),
        'seconds': seconds,
    }

    req = requests.post(TIMERUSH_URL+'/register/',
            data=json.dumps(data)
            )

    print req.json()


def unregister(key):
    data = {
        'key': key        
    }

    req = requests.post(TIMERUSH_URL+'/unregister/',
            data=json.dumps(data)
            )

    print req.json()


if __name__ == '__main__':
    action = sys.argv[1]
    if action == '1':
        time_range = int(sys.argv[2])
        amount = int(sys.argv[3])
        for i in range(amount):
            register(random.randint(1, time_range))
    else:
        unregister(sys.argv[2])


