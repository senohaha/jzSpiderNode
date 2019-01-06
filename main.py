# coding: utf-8
#!/usr/bin/env python

from twisted.scripts.twistd import run
from os.path import join, dirname
from sys import argv
import sys
import scrapyd
import urllib2
import json
import random, string
import hashlib
import requests
import ConfigParser

def genRandomString(slen=16):
    return ''.join(random.sample(string.ascii_letters + string.digits, slen))
# http://39.105.42.151:8080/jzSpiderCMS/api/admin/config/node_get
# http://192.168.20.111:8080/jzSpiderCMS
def get_setting(domain,appId='3003716925983325',key='fnVigs15iwgwBYJxkaNCCGT8NtMzykwG'):
    url = '{domain}/api/admin/config/dispatch_url.jspx'.format(domain=domain)
    rand = genRandomString()
    str = "appId={appId}&nonce_str={random}&type=0&key={key}".format(random=rand, appId=appId, key=key)
    m = hashlib.md5()  # 创建md5对象
    m.update(str.encode())  # 生成加密串
    result = m.hexdigest()  # 打印经过md5加密的字符串
    result = result.upper()
    response = requests.post(url, data={'nonce_str': rand, 'appId': appId, 'sign': result,'type':0})
    # response = requests.get('http://183.223.236.38:19090/jzSpiderCMS/api/admin/config/node_get.jspx?appId=3003716925983325&nonce_str={a}&sign={b}'.format(a=rand,b=result))
    if response.status_code != 200:
        print response.text
        return
    setting = response.text
    print setting, 'dddddd !!!!!!'
    json_set = json.loads(setting)

    dispatcherConfig = json_set['body']['dispatcherConfig']
    dispatch_host = dispatcherConfig['host']
    fp = 'setting.conf'
    conf = ConfigParser.ConfigParser()
    conf.add_section('dispatch')
    conf.set('dispatch', 'dispatch_host', dispatch_host)   #  调度器所在的ip&port
    # conf.set('dispatch', 'dispatch_port', 9090)

    with open(fp, 'w') as fw:
        conf.write(fw)

def get_id():        # 向调度器发起请求，获取ID, 并写入配置文件
    fp = 'setting.conf'
    conf = ConfigParser.ConfigParser()
    conf.read(fp)
    dispatch_host = conf.get('dispatch', 'dispatch_host')
    # dispatch_port = conf.getint('dispatch', 'dispatch_port')
    # dispatch_port = 6800
    url = '{host}/getid'.format(host=dispatch_host)
    print url
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    message = res.read()
    print message, 'message'
    message_json = json.loads(message)
    slave_id = message_json['slave_id']
    conf.add_section('slave_id')
    conf.set('slave_id', 'slave_id', slave_id)
    with open(fp, 'w') as fw:
        conf.write(fw)


def main():
    argv[1:] = ['-n', '-y', join(dirname(scrapyd.__file__), 'txapp.py')]
    print 'lll'
    run()
    print 'kkk'

if __name__ == '__main__':
    # domian = sys.argv[1]
    print 'sss'
    get_setting(domain='http://10.195.112.11:9090/jzSpiderCMS')
    get_id()
    main()

