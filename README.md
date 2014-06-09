# TimeRush

定时器框架， 基于Gevent

*   **Backend**
    
    对定时任务做存储

    需要实现的方法:
    *   add - 保存一个新的任务
    *   remove - 删除一个任务
    *   run - 启动初始化

*   **Interface**

    接受请求，发送通知
    
    需要实现的方法
    *   run - 启动初始化，接受请求
    *   notify - 定时器到时后的通知

## 特性

*   简单易用
    
    目前是基于redis为backend, http作为interface的实现。
    代码简单，log详细，容易debug

*   高可靠性

    无论是TimeRush自身，还是待通知系统崩溃后，
    再次启动后，已完成定时器还是会发送通知。

*   易于扩展

    每个TimeRush作为独立节点，可以组成集群,
    便可容纳海量的定时任务



## Benchmark

*   定时器时间差:   触发时间于设定时间之差。表示延时秒数。0就是没有误差

    测量的是收到callback之后的时间，而不是TimeRush发送通知的时间

*   数量:   多少定时器是这个时间差
*   百分比：这些定时器与总定时器数量的比值

### 1个TimeRush节点

100 个定时器， 时间分散在 1- 60秒

定时器时间差 | 数量 | 百分比
-------------|------|--------
0            | 98   | 98%
1            | 2    | 2%


----------


10000 个定时器，时间分散在 1 - 600秒

定时器时间差 | 数量 | 百分比
-------------|------|--------
0            | 9887 | 98.9%
1            | 113  | 1.1%


----------


10000 个定时器，时间分散在 1 - 60秒

定时器时间差 | 数量 | 百分比
-------------|------|--------
0            | 4584 | 45.8%
1            | 4609 | 46.1%
2            | 514  | 5.1%
3            | 293  | 3%

### 4个TimeRush节点

10000 个定时器，时间分散在 1 - 60秒

定时器时间差 | 数量 | 百分比
-------------|------|--------
0            | 4560 | 45.6%
1            | 5440 | 54.4%




## Protocol

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
            'ret': integer,
            'data': {                               # only exist when you wanna start a new timer
                'callback_cmd': callback_cmd,
                'callback_data': callback_data,
                'seconds': seconds,
            }
        }



