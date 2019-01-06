# -*- coding: utf-8 -*-

import redis
from collections import OrderedDict
import json
# r = redis.StrictRedis(host='192.168.20.115', port=6379, password='jzspider')
r = redis.StrictRedis(host='192.168.20.111', port=6379, )
# map = {'aa':'aaa','dd':'ddd'}
# r.hset('hash','maxNode','4')
# r.hmset('hash',map)

jsondata = {
    "opList": [
        {
            "op_param": {
                "param_list": [
                    "http://www.baidu.com",
                    "http://www.qq.com",
                    "http://www.360.com"
                ]
            },
            "op_setting": {
                "alias": "循环",
                "ifBreakAfterTime": False,
                "loopNum": 0,
                "loopWay": 4,
                "waitElem": "",
                "waitTime": 3
            },
            "op_type": 7,
            "sub_opList": [
                {
                    "op_param": {
                        "URL": "http://www.qq.com"
                    },
                    "op_setting": {
                        "CookieText": "",
                        "alias": "打开网页",
                        "ifBlockAD": False,
                        "ifCleanCookie": False,
                        "ifLoop": True,
                        "ifMovepage": False,
                        "ifRedefCookie": False,
                        "ifRetryOpen ": False,
                        "timeout": 5
                    },
                    "op_type": 1
                },
                {
                    "op_param": {
                        "elem_list": [
                            {
                                "default": "hehe no data",
                                "elemXpath": "",
                                "name": "网页标题1",
                                "strategy": 0,
                                "valueType": 5
                            },
                            {
                                "default": "hehe no data",
                                "elemXpath": "",
                                "name": "网页标题2",
                                "strategy": 0,
                                "valueType": 5
                            },
                            {
                                "default": "hehe no data",
                                "elemXpath": "",
                                "name": "网页标题3",
                                "strategy": 0,
                                "valueType": 5
                            },
                            {
                                "default": "hehe no data",
                                "elemXpath": "",
                                "name": "网页标题4",
                                "strategy": 0,
                                "valueType": 5
                            },
                            {
                                "default": "hehe no data",
                                "elemXpath": "",
                                "name": "网页标题5",
                                "strategy": 0,
                                "valueType": 5
                            },
                            {
                                "default": "hehe no data",
                                "elemXpath": "",
                                "name": "网页标题6",
                                "strategy": 0,
                                "valueType": 5
                            }
                        ]
                    },
                    "op_setting": {
                        "alias": "采集数据",
                        "waitElem": "",
                        "waitTime": 3
                    },
                    "op_type": 3
                }
            ]
        }
    ],
    "title": "新建任务"
}


# jsonstr = json.dumps(jsondata)
# r.hset('task:1:1:desc', 'taskDescription', jsonstr)



r.lpush('task:1:1:urllist', "http://www.baidu.com", "http://www.qq.com", "http://www.360.com")


# def openWeb(jsondata):
#     print jsondata['op_type']
#
#
# taskDesc = r.hget('task:8:2:desc', 'taskDescription')
# # print taskDesc
# r = redis.StrictRedis(host='192.168.20.111', port=6379, )
# r.hset('task:1:1:desc', 'taskDescription', taskDesc)
# json_task = json.loads(taskDesc, object_pairs_hook=OrderedDict)
#
# print json_task
# op_list = json_task['opList'][0]
# subOpNode = op_list['sub_opList']
# for opNode in subOpNode:
#     op_type = opNode['op_type']
#     if op_type == 1:
#         openWeb(opNode)
#     elif op_type == 3:
#         print '343'