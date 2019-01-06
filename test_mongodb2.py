# -*- coding: utf-8 -*-
import pymongo
server = pymongo.MongoClient(host='10.195.112.14', port=27017)
db = server['spider']
col = db['coll']
print col.insert({'4444':'999'})