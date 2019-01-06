# -*- coding: utf-8 -*-
from zope.interface import implementer
from six import iteritems
from twisted.internet.defer import DeferredQueue, inlineCallbacks, maybeDeferred, returnValue

from .utils import get_spider_queues
from .interfaces import IPoller

import fcntl
import struct

import redis
import socket
from scrapyd.webservice import ListJobs
import requests
from twisted.application.service import IServiceCollection
import platform
import sys
import urllib2
import json
import ConfigParser
from urllib2 import Request
import requests


#  爬虫管理器
@implementer(IPoller)
class TaskPoller(object):

    def __init__(self, config, app):
        self.app = app
        self.config = config
        self.update_projects()
        self.dq = DeferredQueue(size=1)
        fp = 'setting.conf'
        conf = ConfigParser.ConfigParser()
        conf.read(fp)
        self.slave_id = conf.get('slave_id', 'slave_id')   # 从配置文件中获取本机的ID
        self.dispatch_host = conf.get('dispatch', 'dispatch_host')
        # self.dispatch_port = conf.getint('dispatch', 'dispatch_port')
        # self.redis_conn = redis.Redis(host='192.168.20.115', port=6379, password='jzspider')



    def poll(self):

        # regex = 'dispatch:{slaveId}:*:*:*'.format(slaveId=SlaveID)
        # for key in self.redis_conn.scan_iter(match=regex):
        #     signal = self.redis_conn.get(key)
        #     userId = key.split(':')[2]
        #     taskId = key.split(':')[3]


        req = Request('{dispatch_host}/hastask?slaveid={slaveid}'.
                      format(slaveid=self.slave_id,
                        dispatch_host=self.dispatch_host))
        res = urllib2.urlopen(req)
        messages = res.read()
        messages_json = json.loads(messages)
        for message in messages_json:
            signal = message['signal']
            userId = message['userId']
            taskId = message['taskId']
            if signal == 'start':  # 启动命令。启动并将该key删除
                app = IServiceCollection(self.app, self.app)
                launcher = app.getServiceNamed('launcher')
                launcher._spawn_process(userId, taskId)
                print '启动命令'
            else:                    # 暂停命令
                url = '{dispatch_host}/stoptask'.format(dispatch_host=self.dispatch_host)
                pid = signal.split('&')[1]
                data = {"slaveId": self.slave_id,
                        "userId": userId,
                        "taskId": taskId,
                        "pid": pid}
                if requests.post(url, data).status_code == 200:
                    print '终止命令'
                else:
                    print '未正常终止'
                # processLiveKey = 'process:{slaveId}:{userId}:{taskId}:{pid}'. \
                #     format(slaveId=self.slave_id, userId=userId, taskId=taskId, pid=pid)
                # self.redis_conn.set(processLiveKey, 'stop')
                # print '终止命令'



    def next(self):
        pass

    def update_projects(self):
        self.queues = get_spider_queues(self.config)

    def _message(self, queue_msg, project):
        d = queue_msg.copy()
        d['_project'] = project
        d['_spider'] = d.pop('name')
        return d


#
@implementer(IPoller)
class QueuePoller(object):

    def __init__(self, config, app):
        self.app = app
        self.config = config
        self.update_projects()
        self.dq = DeferredQueue(size=1)
        fp = 'setting.conf'
        conf = ConfigParser.ConfigParser()
        conf.read(fp)
        self.slave_id = conf.get('slave_id', 'slave_id')  # 从配置文件中获取本机的ID
        self.dispatch_host = conf.get('dispatch', 'dispatch_host')
        # self.dispatch_port = conf.getint('dispatch', 'dispatch_port')

        # self.redis_conn = redis.Redis(host='10.195.112.13', port=6379, password='jzspider')
        self.node_info = {'ip': '',
                          'slaveid': '',
                          'operator': '',
                          'os': '',
                          'cpu': '',
                          'RAM': '',
                          'version':'',
                          'cpuUsed':'',
                          'RAMUsed':'',
                          'netCon':''}
        # self.node_info['ip'] = get_local_ip()
        self.node_info['slaveid'] = self.slave_id
        self.node_info['os'] = sys.platform
    @inlineCallbacks
    def poll(self):
        app = IServiceCollection(self.app, self.app)
        launch = app.getServiceNamed('launcher')
        cur_pro_num = len(launch.processes)
        # print cur_pro_num, 'fffffffssss'

        key = "stats:{m}:info".format(
            m=self.slave_id)

        redishget_url = '{dispatch_host}/redishset'. \
            format(dispatch_host=self.dispatch_host)
        redishget_data = {"key": key, "field": "cur_pro_num", "value": cur_pro_num}
        requests.post(redishget_url, redishget_data)   # self.redis_conn.hset(key, cur_pro_num, 'self.node_info')

        redisexpire_url = '{dispatch_host}/redisexpire'. \
            format(dispatch_host=self.dispatch_host)
        redisexpire_data = {"key": key, "time": 10}
        requests.post(redisexpire_url, redisexpire_data)   #self.redis_conn.expire(key, 10)



        if self.dq.pending:
            return
        for p, q in iteritems(self.queues):
            c = yield maybeDeferred(q.count)
            if c:
                msg = yield maybeDeferred(q.pop)
                if msg is not None:  # In case of a concurrently accessed queue
                    returnValue(self.dq.put(self._message(msg, p)))
        # print 22


    def next(self):
        return self.dq.get()

    def update_projects(self):
        self.queues = get_spider_queues(self.config)

    def _message(self, queue_msg, project):
        d = queue_msg.copy()
        d['_project'] = project
        d['_spider'] = d.pop('name')
        return d


def get_local_ip(ifname='enp1s0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
    return socket.inet_ntoa(inet[20:24])
