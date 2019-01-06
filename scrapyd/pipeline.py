# coding=utf-8
import pymongo
import redis
import time
from redis import WatchError
class Event(object):

    def __init__(self, userId, taskId):
        # self.driver = webdriver.Firefox()
        # self.wait = WebDriverWait(self.driver, 10)

        self.server = pymongo.MongoClient(host='192.168.20.114', port=27017)
        self.db = self.server['spider_data']
        collection = 'user_{userId}_{taskId}'.format(userId=userId, taskId=taskId)
        self.db = self.db[collection]

        self.redis_conn = redis.Redis(host='192.168.20.114', port=6379)
        self.key = "task:{userId}:{taskId}:desc".format(userId=userId, taskId=taskId)
    def extract_data(self, a,b):

        item = {}
        item[a] = 'aa'
        item[b] = 'hh'
        # 查询MongoDB该数据是否已经存在
        flag_repeatCount = False
        if self.db.find_one(item) is None:   # 不存在
            self.db.insert(item)
            print 'insert', item
        else:                                  # 该记录重复
            flag_repeatCount = True
            print '该记录重复，舍弃'

        # 更新redis 字段dataCount, repeatCount
        self._lock_insert_redis(self.key, flag_repeatCount)

    def _lock_insert_redis(self, key, flag_repeatCount):      # 同步锁 向redis数据库插入数据（task:userId:taskId:desc）中的dataCount,repeatCount
        """
        :param key:
        :param flag_repeatCount: 是否对该字段加1，true加1
        :return:
        """

        with self.redis_conn.pipeline() as pipe:
            while 1:
                try:
                    pipe.watch(key)
                    dataCount = pipe.hget(key, 'dataCount')
                    dataCount = int(dataCount) + 1

                    if flag_repeatCount is True:
                        repeatCount = pipe.hget(key, 'repeatCount')
                    pipe.multi()
                    if flag_repeatCount is True:
                        pipe.hset(key, 'repeatCount', int(repeatCount) + 1)
                    pipe.hset(key, 'dataCount', dataCount)
                    pipe.execute()
                    break
                except WatchError:
                    continue
                except Exception:
                    print 'redis 操作异常'
                    break


if __name__ == '__main__':
    dd = Event(1, 1)
    for i in range(20):
        dd.extract_data(str(i), str(i+1))
        time.sleep(5)