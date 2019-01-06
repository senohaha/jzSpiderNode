# -*-coding:utf-8-*-
# !/usr/bin/evn python

import time
from selenium import webdriver
import sys, os
import redis
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
SlaveId = 1

# def main():
#     # running = True
#     #
#     # while running:
#     #     print 'dfy'
#     #     input = sys.stdin.readline().rstrip('\n')
#     #     if input == 'q':
#     #         running = False
#     #     print "You said:%s" % input
#     for i in range(40):
#         import time
#         time.sleep(5)
#         print 'sss   ',i

#
# class Execute(object):
#     # def __init__(self, appid, crawlid):
#     #     self.event = Event(appid, crawlid)
#
#     def execute(self, appid, crawlid):
#         print 'real process:   ', os.getpid()
#         print appid, crawlid, 'aaaaasddfd'
#         driver = webdriver.Firefox()
#         time.sleep(10)

class Execute():
    def __init__(self):
        self.redis_conn = redis.Redis()

    def execute(self, userId, taskId):
        # 轮询redis该用户该任务的子任务队列‘task:{userId}:{taskId}:urllist’
        pid = os.getpid()   # ?与protocol一致否？？？？？

        urllistkey = 'task:{userId}:{taskId}:urllist'.format(userId=userId, taskId=taskId)
        processLiveKey = 'process:{slaveId}:{userId}:{taskId}:{pid}'. \
            format(slaveId=SlaveId, userId=userId, taskId=taskId, pid=pid)
        while True:
            if self.redis_conn.get(processLiveKey) == 'stop':
                break
            if self.redis_conn.llen(urllistkey) is 0:
                break
            url = self.redis_conn.lpop(urllistkey)
            print 'runing a url------','url:', url, ' | pid:', pid
            time.sleep(30)
            print 'end a url------','url:', url, ' | pid:', pid



if __name__ == "__main__":
    userId = sys.argv[1]
    taskId = sys.argv[2]
    # print appid
    # print crawlid
    Execute().execute(userId, taskId)
