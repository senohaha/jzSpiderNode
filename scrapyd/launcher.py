# -*-coding:utf-8-*-
import sys
from datetime import datetime
from multiprocessing import cpu_count

from twisted.internet import reactor, defer, protocol, error
from twisted.application.service import Service
from twisted.python import log
import redis
import os
from scrapyd.utils import get_crawl_args, native_stringify_dict
from scrapyd import __version__
from .interfaces import IPoller, IEnvironment
import ConfigParser
import requests

SlaveID = 1

class Launcher(Service):

    name = 'launcher'

    def __init__(self, config, app):
        self.processes = []
        self.finished = []
        self.finished_to_keep = config.getint('finished_to_keep', 100)
        self.max_proc = self._get_max_proc(config)
        self.runner = config.get('runner', 'scrapyd.runner')
        self.app = app

    def startService(self):
        for slot in range(self.max_proc):
            self._wait_for_project(slot)
        log.msg(format='Scrapyd %(version)s started: max_proc=%(max_proc)r, runner=%(runner)r',
                version=__version__, max_proc=self.max_proc,
                runner=self.runner, system='Launcher')

    def _wait_for_project(self, slot):
        poller = self.app.getComponent(IPoller)
        # poller.next().addCallback(self._spawn_process, slot)

    def _spawn_process(self, userId, taskId):
        # msg = native_stringify_dict(message, keys_only=False)
        # project = msg['_project']
        # args = [sys.executable, '-m', self.runner, 'crawl']
        # args += get_crawl_args(msg)
        # e = self.app.getComponent(IEnvironment)
        # env = e.get_environment(msg, slot)
        # env = native_stringify_dict(env, keys_only=False)
        # pp = ScrapyProcessProtocol(slot, project, msg['_spider'], \
        #     msg['_job'], env)
        # pp.deferred.addBoth(self._process_finished, slot)
        # reactor.spawnProcess(pp, sys.executable, args=args, env=env)
        # self.processes[slot] = pp
        arg = ['/usr/bin/python2.7', '/data/jzSpiderNode/scrapyd/eventnewtest.py', userId, taskId]

        pp = ScrapyProcessProtocol('slot', userId, taskId, 'job', 'env')
        pp.deferred.addBoth(self._process_finished, pp)

        env = os.environ.copy()
        env['PYTHONPATH'] = os.pathsep.join(sys.path)

        reactor.spawnProcess(pp, '/usr/bin/python2.7', arg, env=env)

        self.processes.append(pp)   # 启动

    def _stop_process(self, userId, taskId, pId):
        pass

    def _process_finished(self, _, pp):
        # process = self.processes.pop(slot)
        # process.end_time = datetime.now()
        # self.finished.append(process)
        # del self.finished[:-self.finished_to_keep] # keep last 100 finished jobs
        # self._wait_for_project(slot)
        self.processes.remove(pp)
        pp.end_time = datetime.now()

    def _get_max_proc(self, config):
        max_proc = config.getint('max_proc', 0)
        if not max_proc:
            try:
                cpus = cpu_count()
            except NotImplementedError:
                cpus = 1
            max_proc = cpus * config.getint('max_proc_per_cpu', 4)
        return max_proc

class ScrapyProcessProtocol(protocol.ProcessProtocol):      # 每个进程独有的守护协议

    def __init__(self, slot, userId, taskId, job, env):
        self.project = None
        self.spider = None
        self.slot = slot
        self.pid = None
        self.userId = userId
        self.taskId = taskId
        self.job = job
        self.start_time = datetime.now()
        self.end_time = None
        self.env = env
        self.logfile = 'SCRAPY_LOG_FILE'
        self.itemsfile = 'SCRAPY_FEED_URI'
        self.deferred = defer.Deferred()

        fp = 'setting.conf'
        conf = ConfigParser.ConfigParser()
        conf.read(fp)
        self.slave_id = conf.get('slave_id', 'slave_id')  # 从配置文件中获取本机的ID
        self.dispatch_host = conf.get('dispatch', 'dispatch_host')

        # self.redis_conn = redis.Redis(host='192.168.20.115', port=6379, password='jzspider')
        self.runningNodeKey = 'task:{userId}:{taskId}:slaveId'.format(userId=userId, taskId=taskId)
        self.value = None
        self.processLiveKey = None

    def outReceived(self, data):
        # pass
        log.msg(data.rstrip(), system="Launcher,%d/stdout" % self.pid)

    def errReceived(self, data):
        log.msg(data.rstrip(), system="Launcher,%d/stderr" % self.pid)

    def connectionMade(self):   # 进程启动时自动调用该函数，将该进程加入所属任务的进程队列redis, 并创建代表该进程的key
        self.pid = self.transport.pid
        self.value = '{slaveId}&{pId}'.format(slaveId=SlaveID, pId=self.pid)

        redislpush_url = '{dispatch_host}/redislpush'. \
            format(dispatch_host=self.dispatch_host)
        redislpush_data = {"key": self.runningNodeKey, "value": self.value}
        requests.post(redislpush_url, redislpush_data)      # self.redis_conn.lpush(self.runningNodeKey, self.value)



        self.processLiveKey = 'process:{slaveId}:{userId}:{taskId}:{pid}'.\
            format(slaveId=SlaveID, userId=self.userId, taskId=self.taskId, pid=self.pid)

        redisset_url = '{dispatch_host}/redisset'. \
            format(dispatch_host=self.dispatch_host)
        redisset_data = {"key": self.processLiveKey, "value": 'start'}
        requests.post(redisset_url, redisset_data)      # self.redis_conn.set(self.processLiveKey, 'start')

        self.log("Process started: ")

    def processEnded(self, status):    # 进程结束，将该进程从所属任务的进程队列删除redis,并删除代表该进程的key

        redislrem_url = '{dispatch_host}/redislrem'. \
            format(dispatch_host=self.dispatch_host)
        redislrem_data = {"key": self.runningNodeKey,"value":self.value,"num":1}
        requests.post(redislrem_url, redislrem_data)    # self.redis_conn.lrem(self.runningNodeKey, self.value, num=1)

        redisdelete_url = '{dispatch_host}/redisdelete'. \
            format(dispatch_host=self.dispatch_host)
        redisdelete_data = {"key": self.processLiveKey}
        requests.post(redisdelete_url, redisdelete_data)    # self.redis_conn.delete(self.processLiveKey)

        if isinstance(status.value, error.ProcessDone):
            self.log("Process finished: ")
        else:
            self.log("Process died: exitstatus=%r " % status.value.exitCode)
        self.deferred.callback(self)

    def log(self, action):
        fmt = '%(action)s project=%(project)r spider=%(spider)r job=%(job)r pid=%(pid)r log=%(log)r items=%(items)r'
        log.msg(format=fmt, action=action, project=self.project, spider=self.spider,
                job=self.job, pid=self.pid, log=self.logfile, items=self.itemsfile)


