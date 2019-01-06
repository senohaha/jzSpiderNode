# coding:utf-8
import redis
import traceback
import uuid
redis_conn = redis.Redis()
# # dispatcj_key = 'dispatch:1:1:1:{uuid}'.format(uuid=str(uuid.uuid1()).split('-')[4])
# # redis_conn.set(dispatcj_key, 'start')
# #
# # urllistkey = 'task:{userId}:{taskId}:urllist'.format(userId=1, taskId=1)
# # redis_conn.lpush(urllistkey,'11111','22222','333333','444444','5555','66666','777777','888','99999','0000')
#
# # regex = 'dispatch:{slaveId}:*:*:*'.format(slaveId=1)
# # for key in redis_conn.scan_iter(match=regex):
# #     print key
# #     dd = redis_conn.get(key)
# #     if dd == 'start':
# #         print 'yes'
# dispatcj_key = 'dispatch:1:1:1:{uuid}'.format(uuid=str(uuid.uuid1()).split('-')[4])
# redis_conn.set(dispatcj_key, 'stop&21454')

# if __name__ == "__main__":
#     with redis_conn.pipeline() as pipe:
#         while 1:
#             try:
#                 #关注一个key
#                 pipe.watch('task:1:1:desc')
#                 count = pipe.hget('task:1:1:desc', 'dataCount')
#                 count = int(count)+1
#                 if count >=0:  # 有库存
#                     # 事务开始
#                     pipe.multi()
#                     pipe.set('dataCount', count)
#                     # 事务结束
#                     pipe.execute()
#                     # 把命令推送过去
#                 break
#             except Exception:
#                 traceback.print_exc()
#                 continue
import sys
LL ='s'
print LL