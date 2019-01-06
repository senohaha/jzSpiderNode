# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchAttributeException, NoSuchElementException, SessionNotCreatedException, \
    WebDriverException
from collections import OrderedDict
import json
import time
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
import time
import uuid
import redis
import re
import threading
import sys
import redis
import os
import requests
import ConfigParser
from redis import WatchError

from threading import Thread

SlaveId = 1

class Event(object):

    def __init__(self, execute ,userId, taskId, proxy):
        self.opts = FirefoxOptions()
        self.opts.add_argument('--headless')


        if proxy is None:
            self.driver = webdriver.Firefox(firefox_options=self.opts)
        else:
            http = str(proxy).split(':')[0]
            port = int(str(proxy).split(':')[1])
            profile = webdriver.FirefoxProfile()
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.http', http)
            profile.set_preference('network.proxy.http_port', port)  # int
            profile.update_preferences()
            self.driver = webdriver.Firefox(firefox_profile=profile, firefox_options=self.opts)

        self.wait = WebDriverWait(self.driver, 10)
        self.execute = execute
        self.userId = userId
        self.taskId = taskId

        # self.server = pymongo.MongoClient(host='192.168.20.115', port=27017)
        # self.db = self.server['spider_data']   # 库
        # collection = 'user_{userId}_{taskId}'.format(userId=userId, taskId=taskId)
        # self.db = self.db[collection]    # 集合

        # self.redis_conn = redis.Redis(host='192.168.20.115', port=6379, password='jzspider')
        self.key = "task:{userId}:{taskId}:desc".format(userId=self.userId, taskId=self.taskId)


    # 1 打开网页  参数的URL,代表循环上的url
    def open_web(self, jsondata, url=None):
        # dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        dictdata = jsondata

        op_settings_dict = dictdata['op_setting']

        timeout = op_settings_dict.get('timeout', 5)
        ifBlockAD = op_settings_dict.get('ifBlockAD', True)

        ifLoop = op_settings_dict.get('ifLoop', False)
        # 如果不使用当前所在循环给的url循环，就用自己的
        if ifLoop is False:
            url = dictdata['op_param']['URL']
        if url is None:
            print '请输入一个链接'

        ifMovepage = op_settings_dict.get('ifMovepage', False)
        if ifMovepage is True:
            # 解析出滚动网页的参数
            movepageConf = op_settings_dict['movepageConf']
            moveSum = movepageConf['moveSum']
            moveSpace = movepageConf['moveSpace']
            moveDir = movepageConf['moveDir']

        ifCleanCookie = op_settings_dict.get('ifCleanCookie', False)
        ifRedefCookie = op_settings_dict.get('ifRedefCookie', False)
        # 执行该动作前 等待参数
        waitTime = op_settings_dict['waitTime']
        waitElem = op_settings_dict['waitElem']
        # 打开前等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem != '':
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '点击元素前，等待超时'
            self.driver.get(url)

        print time.time()
        if ifCleanCookie is True:
            self.driver.delete_all_cookies()
        if ifRedefCookie is True:  # 使用用户自定义的cookie
            CookieText = op_settings_dict.get('CookieText', None)
            cookie_list = CookieText.split('\n')
            for cookie_str in cookie_list:
                k_v = cookie_str.split('===')
                key = k_v[0]
                value = k_v[1]
                # print key,':',value
                self.driver.add_cookie({'name': key, 'value': value})
            self.driver.get(url)

        ifRetryOpen = op_settings_dict.get('ifRetry',  False)

        # 2 点击事件  参数elemXpath是循环传来的
    def click(self, jsondata, elemXpath=None):
        dictdata = jsondata
        op_settings_dict = dictdata['op_setting']
        # 执行该动作前 等待参数
        waitTime = op_settings_dict['waitTime']
        waitElem = op_settings_dict['waitElem']
        # 是否点击当前循环中设置的元素 ？ 默认不使用

        ifLoop = op_settings_dict.get('ifLoop', False)
        # 是否在新标签中打开网页
        # ifOpeninnewlabel = op_settings_dict['ifOpeninnewlabel']
        # 是否加载完页面后滚动网页 及 参数
        # ifMovepage = op_settings_dict['ifMovepage']

        if ifLoop is False:
            # 点击元素的xpath
            elemXpath = dictdata['op_param']['elemXpath']

        # 是否重试点击元素
        ifRetryClick = op_settings_dict['ifRetryOpen']
        #
        # 点击元素前等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem != '':
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '点击元素前，等待超时'
        # 在新页面打开？
        # if ifOpeninnewlabel:
        #     pass
        # 滚动页面
        # if ifMovepage:
        #     movePageconf = op_settings_dict['movePageconf']
        #     moveSum = movePageconf['moveSum']
        #     moveSpace = movePageconf['moveSpace']
        #     moveDir = movePageconf['moveDir']
        #     for i in range(moveSum):
        #         js = "document.documentElement.scrollTop=" + str(1000 * (i + 1)) + ""
        #         self.driver.execute_script(js)
        #         time.sleep(moveSpace)
        # 点击元素
        try:
            if ifLoop is False:
                element = WebDriverWait(self.driver, 10, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, elemXpath)))
                element.click()
            else:
                elemXpath.click()
        except TimeoutException as e:  # 超时重新点击
            if ifRetryClick:
                retryClickConf = op_settings_dict['retryClickConf']
                ifUrlContain = retryClickConf['ifUrlContain']
                ifUrlNoContain = retryClickConf['ifUrlNoContain']
                ifTextContain = retryClickConf['ifTextContain']
                ifTextNoContain = retryClickConf['ifTextNoContain']
                ifXpathContain = retryClickConf['ifXpathContain']
                ifXpathNoContain = retryClickConf['ifXpathNoContain']
                retryTime = retryClickConf['retryTime']
                retryDelay = retryClickConf['retryDelay']

                # ？？？
                for i in range(retryTime):
                    try:
                        element = WebDriverWait(self.driver, 10, 0.5).until(
                            EC.presence_of_element_located((By.XPATH, elemXpath)))
                        element.click()
                        break
                    except TimeoutException:
                        time.sleep(retryDelay)
                        continue
            else:
                print "定位不到要点击的元素"

    # 3.提取数据(负责提取一条记录/文档)并插入数据库     参数count为处于第几次循环  参数loop_xpath,外层的xpath
    def extract_data(self, jsondata, count=None, loop_xpath=None):
        # dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        dictdata = jsondata
        op_settings_dict = dictdata['op_setting']
        # 执行该动作前 等待参数
        waitTime = op_settings_dict['waitTime']
        waitElem = op_settings_dict['waitElem']
        # 等待
        if waitTime != 0:
            time.sleep(waitTime)
        if waitElem != '':
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '提取数据前，等待超时'

        # 是否点击当前循环中设置的元素 ？
        ifLoop = op_settings_dict.get('ifLoop', False)

        op_param_dict = dictdata['op_param']
        # 需要提取的所有字段
        elem_list = op_param_dict['elem_list']
        # 用于存提取的文档item = {'学校':'山东大学','代码':'123456','地址':'aaaaa'}
        item = {}
        for elem_dict in elem_list:
            # 每个字段的参数
            name = elem_dict['name']
            useRelativeXpath = elem_dict['useRelativeXpath']   # 给的是否为相对
            # elemXpath = elem_dict['elemXpath']
            # 对本动作在循环中做处理  , 有的字段可能在当前循环下，有的不在

            if loop_xpath is not None:
                # '/html/ul/li[position()>0]' ->'/html/ul'
                list = loop_xpath.split('/')
                pop = list.pop()
                pre_loop_xapth = '/'.join(list)
                position = ''
                for i in pop:
                    if i != '[':
                        position += i
                    else:
                        break
                temp = '[position()=%s]' % count
                position += temp
                elemXpath_pre = pre_loop_xapth + '/' + position  # /html/ul/li[position()=count]


                # elemXpath = '/html/ul/li[position()>0]/div/div[3]/a/em' ->'/html/ul/li[position()=count]/div/div[3]/a/em'
                if useRelativeXpath is False:   # 使用绝对xpath,使用绝对xpath时不和循环xpath拼接
                    elemXpath = elem_dict.get('absoluteXpath', None)

                # loop_xpath = "/html/body/div[position()=6]/div/div/div[position()=1]/table/tbody/tr[position()>1]"
                # relativeXpath = '/td'
                else:   # 使用相对xpath，需要与外层循环xpath进行拼接
                    relativeXpath = elem_dict['relativeXpath']
                    elemXpath = elemXpath_pre + relativeXpath
                    print elemXpath, '采集的xpath!!!!'
                """
                # 给出的是绝对xpath  但又需与循环拼接的情况
                if pre_loop_xapth in elemXpath:   # 如果该字段的xpath在循环中

                    aa = elemXpath[len(pre_loop_xapth):].split('/')
                    aa.pop(0)
                    aa.pop(0)
                    elemXpath_suf = '/'.join(aa)
                    elemXpath = elemXpath_pre+'/'+elemXpath_suf
                """

                # 不在循环的不做处理


            valueType = int(elem_dict['valueType'])
            unfind_dict = elem_dict.get('unfind', None)
            default = elem_dict['default']
            strategy = int(elem_dict['strategy'])

            ifSetNull = False
            ifSetAllNull = False
            useDefault = default
            if strategy == 0:
                ifSetNull = True
            elif strategy == 1:
                ifSetAllNull = True

            try:
                if valueType == 9:   # 或取当前网页标题  不需等待xpath是否存在
                    item[name] = self.driver.title
                else:
                    # 等待此xpath的出现
                    WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, elemXpath)))
                    # 出现后爬取
                    if valueType == 0:
                        item[name] = self.driver.find_element(By.XPATH, elemXpath).get_attribute('attribute')
                    elif valueType == 1:   # 文本
                        item[name] = self.driver.find_element(By.XPATH, elemXpath).text
                    elif valueType == 2:  # 链接
                        print elemXpath, 'hahah'
                        href = self.driver.find_element(By.XPATH, elemXpath).get_attribute('href')
                        src = self.driver.find_element(By.XPATH, elemXpath).get_attribute('src')
                        if href is not None:
                            item[name] = href
                        else:
                            item[name] = src
                    elif valueType == 3:  # 抓取选项中的文本
                        pass
                    elif valueType == 4:  # 抓取outerHtml
                        item[name] = self.driver.find_element(By.XPATH, elemXpath).get_attribute('outerHTML')
                    elif valueType == 5:  # 抓取input标签的value属性
                        item[name] = self.driver.find_element(By.XPATH, elemXpath).get_attribute('value')
                    elif valueType == 6:  # 抓取超链接
                        pass
                    elif valueType == 7:  # innerHTML
                        item[name] = self.driver.find_element(By.XPATH, elemXpath).get_attribute('innerHTML')
                    elif valueType == 8:  # 页面网址
                        pass
                    elif valueType == 10:  # 从页面源码中提取
                        pass
                    elif valueType == 11:  # 生成固定值
                        pass
                    elif valueType == 12:  # 使用当前时间
                        pass




            except TimeoutException as e:
                # 找不到该字段的处理方式
                if ifSetNull:
                    item[name] = None
                elif useDefault is not None:
                    item[name] = useDefault

        # 查询MongoDB该数据是否已经存在
        flag_repeatCount = False

        url = '{dispatch_host}/mongofindone'. \
            format(dispatch_host=self.execute.dispatch_host)
        item1 = json.dumps(item)
        data = {"userId": self.userId,
                "taskId": self.taskId,
                "item": item1}
        print url, 'url@@@@@@@@@@@@@@'
        print requests.post(url, data).text,'&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
        if json.loads(requests.post(url, data).text)['find_one'] is True:   # bu cun  zai
            flag_repeatCount = False
            item['isExport'] = 0
            item1 = json.dumps(item)
            url = '{dispatch_host}/mongoinsert'. \
                format(dispatch_host=self.execute.dispatch_host)
            data = {"userId":self.userId,
                    "taskId": self.taskId,
                    "item": item1}
            requests.post(url, data)    # self.db.insert(item)

            print '$$$$$$insert%%%%!!!!', item
        else:                                  # 该记录重复
            flag_repeatCount = True

            print '$$$$$repeat#######!!!!', item

        # 更新redis 字段dataCount, repeatCount
        print flag_repeatCount,'jzSpider!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!flag_repeatCount'
        url = '{dispatch_host}/lockinsertredis'.\
            format(dispatch_host=self.execute.dispatch_host)
        data = {"key": self.key, "flag_repeatCount": flag_repeatCount}
        requests.post(url, data)
        # self._lock_insert_redis(self.key, flag_repeatCount)



    # 4 输入文本
    def input_text(self, jsondata):
        # dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        dictdata = jsondata
        op_settings_dict = dictdata['op_setting']
        # 执行该动作前 等待参数
        waitTime = op_settings_dict['waitTime']
        waitElem = op_settings_dict['waitElem']
        # 等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem !='':
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '输入文本前，等待超时'

        # 是否点击当前循环中设置的元素 ？
        ifLoop = op_settings_dict['ifLoop']

        op_param_dict = dictdata['op_param']
        elemXpath = op_param_dict['elemXpath']
        text = op_param_dict['text']
        try:
            inputtext = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, elemXpath)))
            inputtext.clear()  # 清除输入框中的内容
            inputtext.send_keys(text.decode('utf-8'))
        except TimeoutException as e:
            print '无法定位到输入框'

    # 5 识别验证码
    def verification_code(self):
        pass

    # 6 循环遍历下拉框  ？
    def loop_option(self):
        # 需要select的xpath
        driver = webdriver.Firefox()
        driver.get('http://sahitest.com/demo/selectTest.htm')

        selectXpath = '//*[@id="s4Id"]'
        select = Select(driver.find_element_by_xpath(selectXpath))
        optionList = select.options
        for option in optionList:
            print option.text

    # 7 循环
    def loop(self, jsondata, splited=False):


        # dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)!!!!!!!!!!!待修改
        dictdata = jsondata
        op_settings_dict = dictdata['op_setting']
        # 执行该动作前 等待参数
        waitTime = op_settings_dict['waitTime']
        waitElem = op_settings_dict['waitElem']

        # 是否按循环次数循环
        ifBreakAfterTime = op_settings_dict['ifBreakAfterTime']
        loopNum = 0
        if ifBreakAfterTime is True:
            # 循环终止次数
            loopNum = op_settings_dict['loopNum']
        # 循环方式
        loopWay = op_settings_dict['loopWay']
        # 根据 不同的循环方式 得到 循环参数 param_list
        op_param_dict = dictdata['op_param']

        param_list = []
        elemXpath = None
        if loopWay == 1:    # 单个元素(循环点击下一页)
            elemXpath = op_param_dict['param']
        elif loopWay == 2:  # 固定元素列表  点击链接
            elemXpath = op_param_dict['param_list']
            param_list = self.driver.find_elements_by_xpath(elemXpath)
        elif loopWay == 3:  # 不固定元素列表   elemXpath 为外循环,如‘/html/div/div([position>0])’
            elemXpath = op_param_dict['param']
            param_list = self.driver.find_elements_by_xpath(elemXpath)

        elif loopWay == 4:  # url列表
            param_list = op_param_dict['param_list']
        elif loopWay == 5:   # 文本列表
            param_list = op_param_dict['param_list']
        else:
            print '循环方式出错'

        sub_opList = dictdata['sub_opList']

        if splited is True:   #  如果本循环的任务被拆分，则一次循环的参数是从redis里获取一条
            pid = os.getpid()
            urllistkey = 'task:{userId}:{taskId}:urllist'.format(userId=userId, taskId=taskId)
            processLiveKey = 'process:{slaveId}:{userId}:{taskId}:{pid}'. \
                format(slaveId=SlaveId, userId=userId, taskId=taskId, pid=pid)
            redisllen_url = '{dispatch_host}/redisllen'. \
                format(dispatch_host=self.execute.dispatch_host)
            redisllen_data = {"key": urllistkey}

            while True:         # 依据从redis中取循环参数循环！！！！

                redisget_url = '{dispatch_host}/redisget'. \
                    format(dispatch_host=self.execute.dispatch_host)
                redisget_data = {"key": processLiveKey}
                if json.loads(requests.post(redisget_url, redisget_data).text)['value'] == 'stop':  #if self.redis_conn.get(processLiveKey) == 'stop':
                    return 'break'
                    # break
                if json.loads(requests.post(redisllen_url, redisllen_data).text)['len'] == 0:    # if self.redis_conn.llen(urllistkey) == 0:
                    return 'break'
                    # break
                redislpop_url = '{dispatch_host}/redislpop'. \
                    format(dispatch_host=self.execute.dispatch_host)
                redislpop_data = {'key': urllistkey}
                url = json.loads(requests.post(redislpop_url, redislpop_data).text)['value']
                # 每次循环的子动作
                for op_node in sub_opList:
                    # op_nodes_dict = json.loads(op_nodes, object_pairs_hook=OrderedDict)
                    # op_node = op_nodes_dict['op_node']
                    # op_node_dict = json.loads(op_node, object_pairs_hook=OrderedDict)
                    op_type = op_node['op_type']
                    if op_type == 1:
                        self.open_web(op_node, url=url)
                    elif op_type == 2:
                        self.click(op_node, elemXpath=url)
                    elif op_type == 3:
                        # 一次循环只是提取当前一个li标签下的数据
                        self.extract_data(op_node)
                    elif op_type == 4:
                        self.input_text(op_node)
                    elif op_type == 5:
                        self.verification_code()  # ?
                    elif op_type == 6:
                        self.loop_option()  # ?
                    elif op_type == 7:
                        self.loop(op_node)
                    elif op_type == 8:
                        self.condition(op_node)

        else:   # 本循环的任务未被拆分
            if loopWay == 1:  # 循环点击单个元素
                pass
            else:           # 依据列表循环
                count = 0
                for i in param_list:  # 依据循环参数循环！！！！
                    count = count + 1
                    # 每次循环的子动作
                    for op_node in sub_opList:
                        # op_nodes_dict = json.loads(op_nodes, object_pairs_hook=OrderedDict)
                        # op_node = op_nodes_dict['op_node']
                        # op_node_dict = json.loads(op_node, object_pairs_hook=OrderedDict)
                        op_type = op_node['op_type']
                        if op_type == 1:
                            self.open_web(op_node, url=i)
                        elif op_type == 2:
                            self.click(op_node, elemXpath=i)
                        elif op_type == 3:
                            # 一次循环只是提取当前一个li标签下的数据
                            self.extract_data(op_node, count=count, loop_xpath=elemXpath)
                        elif op_type == 4:
                            self.input_text(op_node)
                        elif op_type == 5:
                            self.verification_code()  # ?
                        elif op_type == 6:
                            self.loop_option()  # ?
                        elif op_type == 7:
                            self.loop(op_node)
                        elif op_type == 8:
                            self.condition(op_node)
        return ''



    # 8 判断条件
    def condition(self, jsondata):
        # dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        dictdata = jsondata
        op_settings_dict = dictdata['op_setting']
        # 执行该动作前 等待参数
        waitTime = op_settings_dict['waitTime']
        waitElem = op_settings_dict['waitElem']
        # 等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem != '':
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '判断条件，等待超时'

        sub_opList = dictdata['sub_opList']
        for op_node in sub_opList:
            # op_node = op_nodes['op_node']
            op_type = op_node['op_type']
            if op_type != 9:
                print '判断条件的子动作必须是条件分支'
                continue
            self.branch(op_node)
            # ??????????????????

    # 9 条件分支
    def branch(self, jsondata):
        # dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict, strict=False)
        dictdata = jsondata
        op_settings_dict = dictdata['op_setting']
        # 执行该动作前 等待参数
        waitTime = op_settings_dict['waitTime']
        waitElem = op_settings_dict['waitElem']
        # 等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem != '':
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '判断条件，等待超时'

        op_param_dict = dictdata['op_param']
        ifElemInIframe = op_param_dict.get('ifElemInIframe', False)
        if ifElemInIframe is True:
            iframeXpath = op_param_dict.get('iframeXpath', None)

        # 以下三个条件只能选一个，作为本分支执行的条件
        condition = op_param_dict.get('condition', '0')
        # if condition == 0:  # 总是执行
        #     pass
        if condition == 1:  # 出现文本
            text = op_param_dict.get('text', None)
            page_source = self.driver.page_source
            if text.decode('utf-8') not in page_source:
                return       # 未出现就返回，不执行该分支
        elif condition == 2:  # 出现元素
            elemXpath = op_param_dict.get('elemXpath', None)
            try:
                self.driver.find_element_by_xpath(elemXpath)
            except Exception:
                return

        # 条件满足执行该分支(子动作列表)
        sub_opList = dictdata['sub_opList']

        # 解析子动作
        self.parse_opList(sub_opList)


    # 解析子动作
    def parse_opList(self, sub_opList):
        for op_node in sub_opList:
            op_type = op_node['op_type']
            if op_type == 1:
                self.open_web(op_node)
            elif op_type == 2:
                self.click(op_node)
            elif op_type == 3:
                self.extract_data(op_node)
            elif op_type == 4:
                self.input_text(op_node)
            elif op_type == 5:
                self.verification_code()
            elif op_type == 6:
                self.loop_option()
            elif op_type == 7:
                self.loop(op_node)
            elif op_type == 8:
                self.condition(op_node)
            elif op_type == 10:
                self.mouse_over()


    # 10 鼠标移动到元素上
    def mouse_over(self):
        pass

    # 关闭driver
    def close(self):
        self.driver.close()

def parse_task():
    pass


# if __name__=='__main__':
#     # driver = webdriver.Firefox()
#     # driver.get('https://www.youzy.cn/college/838/newplan.html')
#     # driver.delete_all_cookies()
#     # driver.add_cookie({'name': 'UM_distinctid', 'value': '1648c6c0af81b9-046504cbf2e5ff-5e442e19-e1000-1648c6c0afa5c2'})
#     # driver.add_cookie({'name': 'Youzy.FirstSelectVersion', 'value': '1'})
#     # driver.add_cookie({'name': 'readlist', 'value': '%5B%7B%22collegeId%22%3A%221242%22%2C%22collegeName%22%3A%22%E8%A5%BF%E5%8D%8E%E5%A4%A7%E5%AD%A6%22%7D%5D'})
#     # driver.add_cookie({'name': 'SERVER_ID', 'value': '1beb241f-f89003c2'})
#     # driver.add_cookie({'name': 'Hm_lvt_12d15b68f4801f6d65dceb17ee817e26', 'value': '1531364249,1531737828'})
#     # driver.add_cookie({'name': 'QIAO_CK_8005644_R', 'value': ''})
#     # driver.add_cookie({'name': 'CNZZDATA1254568697', 'value': '172074776-1531359450-%7C1531737737'})
#     # driver.add_cookie({'name': 'Youzy.CurrentVersion', 'value': '%7b%22Name%22%3a%22%e5%ae%81%e5%a4%8f%22%2c%22EnName%22%3a%22nx%22%2c%22ProvinceId%22%3a862%2c%22Domain%22%3a%22http%3a%2f%2fnx.youzy.cn%22%2c%22Description%22%3a%22%22%2c%22QQGroup%22%3a%22201679097%22%2c%22QQGroupUrl%22%3anull%2c%22IsOpen%22%3atrue%2c%22Sort%22%3a25%2c%22Province%22%3a%7b%22Name%22%3a%22%e5%ae%81%e5%a4%8f%22%2c%22Id%22%3a862%7d%2c%22Id%22%3a27%7d'})
#     # driver.add_cookie({'name': 'Uzy.AUTH', 'value': 'E9B817CF559620D8C603B058D329364FF1CBD9416A49EE44A76F0D426437E6A32408436332B6C699DE0AC236BA07F8D3B10956D2B3FDA51DDED8372BE3043D8061DEC009BE5AE0C99D64503545ADDD8F2AC66C06CE4BF627F82E13D084813439D822DB641DF76052E05E8B1ACD2E2353D4063777EA2B5EB2ADAEDA7F762D73B7'})
#     # a = str(int(time.time()))
#     # print a
#     # driver.add_cookie({'name': 'Hm_lpvt_12d15b68f4801f6d65dceb17ee817e26', 'value': a})
#     #
#     #
#     # driver.get('https://www.youzy.cn/college/838/newplan.html')
#     json_1 = '{'\
# 											'"op_type": 2,'\
# 											'"op_setting":{'\
# 												'"alias":"点击元素",'\
# 												'"waitConf":{'\
# 													'"waitTime":0,'\
# 													'"waitElem":null'\
# 												'},'\
# 												'"ifLoop":true,'\
# 												'"ifOpeninnewlabel":false,'\
# 												'"ifAjax": true,'\
# 												'"AjaxOvertime": 2000,'\
# 												'"ifMovepage":false,'\
# 												'"ifRetryClick":false' \
#              '},'\
# 											'"op_param":null,'\
# 											'"sub_opList":[]' \
#              '}'
#     a = Event('q', 'd')
#     a.driver.get('https://s.taobao.com/search?q=python&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20180828&ie=utf8')
#     waixpath = '/html/body/div[1]/div[2]/div[3]/div[1]/div[21]/div/div/div[1]/div[position()>0]/div[2]/div[2]/a'
#     lis = a.driver.find_elements_by_xpath(waixpath)
#     for i in lis:
#         a.click(json_1, i)

class Execute():
    def __init__(self):
        fp = 'setting.conf'
        conf = ConfigParser.ConfigParser()
        conf.read(fp)
        self.slave_id = 1 #conf.get('slave_id', 'slave_id')  # 从配置文件中获取本机的ID
        # self.dispatch_host = '60.205.186.105'
        self.dispatch_host = conf.get('dispatch', 'dispatch_host')
        # self.dispatch_port = 6800#conf.getint('dispatch', 'dispatch_port')

        # self.redis_conn = redis.Redis('192.168.20.115', port=6379, password='jzspider')

    def execute(self, userId, taskId):
        # 轮询redis该用户该任务的子任务队列‘task:{userId}:{taskId}:urllist’
        pid = os.getpid()   # ?与protocol一致否？？？？？

        taskDescKey = 'task:{userId}:{taskId}:desc'.format(userId=userId, taskId=taskId)
        urllistkey = 'task:{userId}:{taskId}:urllist'.format(userId=userId, taskId=taskId)
        processLiveKey = 'process:{slaveId}:{userId}:{taskId}:{pid}'. \
            format(slaveId=SlaveId, userId=userId, taskId=taskId, pid=pid)

        # 从ip池随机取出一个ip
        redisgetproxy_url = '{dispatch_host}/getproxy'. \
            format(dispatch_host=self.dispatch_host)
        proxy = json.loads(requests.post(redisgetproxy_url).text)['proxy']

        self.event = Event(self, userId, taskId, proxy)

        redisllen_url = '{dispatch_host}/redisllen'. \
            format(dispatch_host=self.dispatch_host)
        redisllen_data = {"key" : urllistkey}



        if json.loads(requests.post(redisllen_url, redisllen_data).text)['len'] == 0:   # if self.redis_conn.llen(urllistkey) == 0:# 任务未拆分
            redishget_url = '{dispatch_host}/redishget'. \
                format(dispatch_host=self.dispatch_host)
            redishget_data = {"key": taskDescKey, "field": "taskDescription"}
            taskDesc = json.loads(requests.post(redishget_url, redishget_data).text)['value']  # taskDesc = self.redis_conn.hget(taskDescKey, 'taskDescription')
            print '任务未拆分'
            print type(taskDesc), '%%%%%%%%%%%%%%%%%%%%%%%'
            json_task = json.loads(taskDesc, object_pairs_hook=OrderedDict, strict=False)   # strict 设为False,允许字符串里有转意字符
            op_list = json_task['opList']
            for op in op_list:
                op_type = op['op_type']
                if op_type == 1:
                    self.event.open_web(op)
                elif op_type == 2:
                    self.event.click(op)
                elif op_type == 3:
                    self.event.extract_data(op)
                elif op_type == 4:
                    self.event.input_text(op)
                elif op_type == 7:
                    self.event.loop(op)
                elif op_type == 8:
                    self.event.condition(op)

        else:  # 拆分
            # while True:
                # redisget_url = 'http://{dispatch_host}:{dispatch_port}/redisget'. \
                #     format(dispatch_host=self.dispatch_host,
                #            dispatch_port=self.dispatch_port)
                # redisget_data = {"key": processLiveKey}
                # if json.loads(requests.post(redisget_url, redisget_data).text)['value'] == 'stop':  #if self.redis_conn.get(processLiveKey) == 'stop':
                #     break
                # if json.loads(requests.post(redisllen_url, redisllen_data).text)['len'] == 0:    # if self.redis_conn.llen(urllistkey) == 0:
                #     break
                # redislpop_url =  'http://{dispatch_host}:{dispatch_port}/redislpop'. \
                #     format(dispatch_host=self.dispatch_host,
                #            dispatch_port=self.dispatch_port)
                # redislpop_data = {'key': urllistkey}
                # url = json.loads(requests.post(redislpop_url, redislpop_data).text)['value']   #  url = self.redis_conn.lpop(urllistkey)


                redishget_url = '{dispatch_host}/redishget'. \
                    format(dispatch_host=self.dispatch_host)
                redishget_data = {"key": taskDescKey, "field": "taskDescription"}
                taskDesc = json.loads(requests.post(redishget_url, redishget_data).text)['value']  #taskDesc = self.redis_conn.hget(taskDescKey, 'taskDescription')

                print type(taskDesc), 'ssss'
                json_task = json.loads(taskDesc, object_pairs_hook=OrderedDict, strict=False)
                op_list = json_task['opList']
                first = True   # 标志是否是第一个循环动作
                for opNode in op_list:
                    op_type = opNode['op_type']
                    if op_type == 1:
                        self.event.open_web(opNode)
                    elif op_type == 2:
                        self.event.click(opNode)
                    elif op_type == 3:
                        self.event.extract_data(opNode)
                    elif op_type == 4:
                        self.event.input_text(opNode)
                    elif op_type == 7:
                        if first is True:          #  默认将第一个循环动作进行拆分
                            aa = self.event.loop(opNode, splited=True)
                            first = False
                            if aa is 'break':
                                break
                        else:
                            self.event.loop(opNode, splited=False)
                    elif op_type == 8:
                        self.event.condition(opNode)
        self.event.close()


if __name__ == "__main__":
    userId = sys.argv[1]
    taskId = sys.argv[2]


    Execute().execute(userId, taskId)
    taskDesc ='''
    {
    "opList": [
        {
            "fixedElementList": "",
            "op_param": {
                "param_list": [
                    "https://www.youzy.cn/sc/",
                    "https://www.youzy.cn/college/1242/cfraction.html ",
                    "https://www.youzy.cn/college/838/cfraction.html ",
                    "https://www.youzy.cn/college/1107/cfraction.html ",
                    "https://www.youzy.cn/college/848/cfraction.html ",
                    "https://www.youzy.cn/college/4248/cfraction.html ",
                    "https://www.youzy.cn/college/939/cfraction.html ",
                    "https://www.youzy.cn/college/926/cfraction.html ",
                    "https://www.youzy.cn/college/4130/cfraction.html ",
                    "https://www.youzy.cn/college/2981/cfraction.html ",
                    "https://www.youzy.cn/college/3708/cfraction.html ",
                    "https://www.youzy.cn/college/1983/cfraction.html ",
                    "https://www.youzy.cn/college/3449/cfraction.html ",
                    "https://www.youzy.cn/college/879/cfraction.html ",
                    "https://www.youzy.cn/college/1177/cfraction.html ",
                    "https://www.youzy.cn/college/839/cfraction.html ",
                    "https://www.youzy.cn/college/3980/cfraction.html ",
                    "https://www.youzy.cn/college/851/cfraction.html ",
                    "https://www.youzy.cn/college/1117/cfraction.html ",
                    "https://www.youzy.cn/college/857/cfraction.html ",
                    "https://www.youzy.cn/college/886/cfraction.html ",
                    "https://www.youzy.cn/college/854/cfraction.html ",
                    "https://www.youzy.cn/college/2985/cfraction.html ",
                    "https://www.youzy.cn/college/898/cfraction.html ",
                    "https://www.youzy.cn/college/4337/cfraction.html ",
                    "https://www.youzy.cn/college/922/cfraction.html ",
                    "https://www.youzy.cn/college/930/cfraction.html ",
                    "https://www.youzy.cn/college/1329/cfraction.html ",
                    "https://www.youzy.cn/college/1141/cfraction.html ",
                    "https://www.youzy.cn/college/843/cfraction.html ",
                    "https://www.youzy.cn/college/909/cfraction.html ",
                    "https://www.youzy.cn/college/1170/cfraction.html ",
                    "https://www.youzy.cn/college/1076/cfraction.html ",
                    "https://www.youzy.cn/college/852/cfraction.html ",
                    "https://www.youzy.cn/college/3209/cfraction.html ",
                    "https://www.youzy.cn/college/885/cfraction.html ",
                    "https://www.youzy.cn/college/835/cfraction.html ",
                    "https://www.youzy.cn/college/3369/cfraction.html ",
                    "https://www.youzy.cn/college/866/cfraction.html ",
                    "https://www.youzy.cn/college/916/cfraction.html ",
                    "https://www.youzy.cn/college/889/cfraction.html ",
                    "https://www.youzy.cn/college/3869/cfraction.html ",
                    "https://www.youzy.cn/college/2025/cfraction.html ",
                    "https://www.youzy.cn/college/908/cfraction.html ",
                    "https://www.youzy.cn/college/995/cfraction.html ",
                    "https://www.youzy.cn/college/840/cfraction.html ",
                    "https://www.youzy.cn/college/844/cfraction.html ",
                    "https://www.youzy.cn/college/873/cfraction.html ",
                    "https://www.youzy.cn/college/1035/cfraction.html ",
                    "https://www.youzy.cn/college/829/cfraction.html ",
                    "https://www.youzy.cn/college/847/cfraction.html ",
                    "https://www.youzy.cn/college/948/cfraction.html ",
                    "https://www.youzy.cn/college/918/cfraction.html ",
                    "https://www.youzy.cn/college/4193/cfraction.html ",
                    "https://www.youzy.cn/college/865/cfraction.html ",
                    "https://www.youzy.cn/college/1012/cfraction.html ",
                    "https://www.youzy.cn/college/971/cfraction.html ",
                    "https://www.youzy.cn/college/1482/cfraction.html ",
                    "https://www.youzy.cn/college/2490/cfraction.html ",
                    "https://www.youzy.cn/college/899/cfraction.html ",
                    "https://www.youzy.cn/college/896/cfraction.html ",
                    "https://www.youzy.cn/college/4171/cfraction.html ",
                    "https://www.youzy.cn/college/1139/cfraction.html ",
                    "https://www.youzy.cn/college/863/cfraction.html ",
                    "https://www.youzy.cn/college/858/cfraction.html ",
                    "https://www.youzy.cn/college/888/cfraction.html ",
                    "https://www.youzy.cn/college/830/cfraction.html ",
                    "https://www.youzy.cn/college/2293/cfraction.html ",
                    "https://www.youzy.cn/college/925/cfraction.html ",
                    "https://www.youzy.cn/college/1055/cfraction.html ",
                    "https://www.youzy.cn/college/1525/cfraction.html ",
                    "https://www.youzy.cn/college/934/cfraction.html ",
                    "https://www.youzy.cn/college/944/cfraction.html ",
                    "https://www.youzy.cn/college/1868/cfraction.html ",
                    "https://www.youzy.cn/college/877/cfraction.html ",
                    "https://www.youzy.cn/college/1143/cfraction.html ",
                    "https://www.youzy.cn/college/859/cfraction.html ",
                    "https://www.youzy.cn/college/3471/cfraction.html ",
                    "https://www.youzy.cn/college/834/cfraction.html ",
                    "https://www.youzy.cn/college/3420/cfraction.html ",
                    "https://www.youzy.cn/college/3472/cfraction.html ",
                    "https://www.youzy.cn/college/955/cfraction.html ",
                    "https://www.youzy.cn/college/1703/cfraction.html ",
                    "https://www.youzy.cn/college/963/cfraction.html ",
                    "https://www.youzy.cn/college/902/cfraction.html ",
                    "https://www.youzy.cn/college/904/cfraction.html ",
                    "https://www.youzy.cn/college/954/cfraction.html ",
                    "https://www.youzy.cn/college/929/cfraction.html ",
                    "https://www.youzy.cn/college/878/cfraction.html ",
                    "https://www.youzy.cn/college/947/cfraction.html ",
                    "https://www.youzy.cn/college/1289/cfraction.html ",
                    "https://www.youzy.cn/college/1010/cfraction.html ",
                    "https://www.youzy.cn/college/872/cfraction.html ",
                    "https://www.youzy.cn/college/3450/cfraction.html ",
                    "https://www.youzy.cn/college/974/cfraction.html ",
                    "https://www.youzy.cn/college/1008/cfraction.html ",
                    "https://www.youzy.cn/college/2493/cfraction.html ",
                    "https://www.youzy.cn/college/3241/cfraction.html ",
                    "https://www.youzy.cn/college/864/cfraction.html ",
                    "https://www.youzy.cn/college/917/cfraction.html ",
                    "https://www.youzy.cn/college/1570/cfraction.html ",
                    "https://www.youzy.cn/college/1689/cfraction.html ",
                    "https://www.youzy.cn/college/2074/cfraction.html ",
                    "https://www.youzy.cn/college/1202/cfraction.html ",
                    "https://www.youzy.cn/college/1300/cfraction.html ",
                    "https://www.youzy.cn/college/1044/cfraction.html ",
                    "https://www.youzy.cn/college/1491/cfraction.html ",
                    "https://www.youzy.cn/college/855/cfraction.html ",
                    "https://www.youzy.cn/college/1045/cfraction.html ",
                    "https://www.youzy.cn/college/1263/cfraction.html ",
                    "https://www.youzy.cn/college/3412/cfraction.html ",
                    "https://www.youzy.cn/college/1558/cfraction.html ",
                    "https://www.youzy.cn/college/3217/cfraction.html ",
                    "https://www.youzy.cn/college/1719/cfraction.html ",
                    "https://www.youzy.cn/college/1511/cfraction.html ",
                    "https://www.youzy.cn/college/2322/cfraction.html ",
                    "https://www.youzy.cn/college/3960/cfraction.html ",
                    "https://www.youzy.cn/college/3476/cfraction.html ",
                    "https://www.youzy.cn/college/1656/cfraction.html ",
                    "https://www.youzy.cn/college/893/cfraction.html ",
                    "https://www.youzy.cn/college/3959/cfraction.html ",
                    "https://www.youzy.cn/college/1060/cfraction.html ",
                    "https://www.youzy.cn/college/1775/cfraction.html ",
                    "https://www.youzy.cn/college/1361/cfraction.html ",
                    "https://www.youzy.cn/college/1417/cfraction.html ",
                    "https://www.youzy.cn/college/2164/cfraction.html ",
                    "https://www.youzy.cn/college/905/cfraction.html ",
                    "https://www.youzy.cn/college/1175/cfraction.html ",
                    "https://www.youzy.cn/college/958/cfraction.html ",
                    "https://www.youzy.cn/college/928/cfraction.html ",
                    "https://www.youzy.cn/college/1003/cfraction.html ",
                    "https://www.youzy.cn/college/1527/cfraction.html ",
                    "https://www.youzy.cn/college/3253/cfraction.html ",
                    "https://www.youzy.cn/college/1130/cfraction.html ",
                    "https://www.youzy.cn/college/932/cfraction.html ",
                    "https://www.youzy.cn/college/915/cfraction.html ",
                    "https://www.youzy.cn/college/2506/cfraction.html ",
                    "https://www.youzy.cn/college/3445/cfraction.html ",
                    "https://www.youzy.cn/college/1127/cfraction.html ",
                    "https://www.youzy.cn/college/849/cfraction.html ",
                    "https://www.youzy.cn/college/1862/cfraction.html ",
                    "https://www.youzy.cn/college/1708/cfraction.html ",
                    "https://www.youzy.cn/college/832/cfraction.html ",
                    "https://www.youzy.cn/college/3661/cfraction.html ",
                    "https://www.youzy.cn/college/2983/cfraction.html ",
                    "https://www.youzy.cn/college/1178/cfraction.html ",
                    "https://www.youzy.cn/college/1182/cfraction.html ",
                    "https://www.youzy.cn/college/1234/cfraction.html ",
                    "https://www.youzy.cn/college/4197/cfraction.html ",
                    "https://www.youzy.cn/college/936/cfraction.html ",
                    "https://www.youzy.cn/college/1360/cfraction.html ",
                    "https://www.youzy.cn/college/964/cfraction.html ",
                    "https://www.youzy.cn/college/1199/cfraction.html ",
                    "https://www.youzy.cn/college/979/cfraction.html ",
                    "https://www.youzy.cn/college/1969/cfraction.html ",
                    "https://www.youzy.cn/college/846/cfraction.html ",
                    "https://www.youzy.cn/college/1439/cfraction.html ",
                    "https://www.youzy.cn/college/975/cfraction.html ",
                    "https://www.youzy.cn/college/3250/cfraction.html ",
                    "https://www.youzy.cn/college/1106/cfraction.html ",
                    "https://www.youzy.cn/college/2081/cfraction.html ",
                    "https://www.youzy.cn/college/1088/cfraction.html ",
                    "https://www.youzy.cn/college/2551/cfraction.html ",
                    "https://www.youzy.cn/college/837/cfraction.html ",
                    "https://www.youzy.cn/college/1021/cfraction.html ",
                    "https://www.youzy.cn/college/827/cfraction.html ",
                    "https://www.youzy.cn/college/1232/cfraction.html ",
                    "https://www.youzy.cn/college/1168/cfraction.html ",
                    "https://www.youzy.cn/college/4102/cfraction.html ",
                    "https://www.youzy.cn/college/1706/cfraction.html ",
                    "https://www.youzy.cn/college/941/cfraction.html ",
                    "https://www.youzy.cn/college/870/cfraction.html ",
                    "https://www.youzy.cn/college/1998/cfraction.html ",
                    "https://www.youzy.cn/college/3354/cfraction.html ",
                    "https://www.youzy.cn/college/3975/cfraction.html ",
                    "https://www.youzy.cn/college/1245/cfraction.html ",
                    "https://www.youzy.cn/college/2367/cfraction.html ",
                    "https://www.youzy.cn/college/3422/cfraction.html ",
                    "https://www.youzy.cn/college/1249/cfraction.html ",
                    "https://www.youzy.cn/college/1354/cfraction.html ",
                    "https://www.youzy.cn/college/3979/cfraction.html ",
                    "https://www.youzy.cn/college/1054/cfraction.html ",
                    "https://www.youzy.cn/college/1087/cfraction.html ",
                    "https://www.youzy.cn/college/1069/cfraction.html ",
                    "https://www.youzy.cn/college/2491/cfraction.html ",
                    "https://www.youzy.cn/college/1184/cfraction.html ",
                    "https://www.youzy.cn/college/2397/cfraction.html ",
                    "https://www.youzy.cn/college/1090/cfraction.html ",
                    "https://www.youzy.cn/college/1693/cfraction.html ",
                    "https://www.youzy.cn/college/1975/cfraction.html ",
                    "https://www.youzy.cn/college/2947/cfraction.html ",
                    "https://www.youzy.cn/college/1970/cfraction.html ",
                    "https://www.youzy.cn/college/1026/cfraction.html ",
                    "https://www.youzy.cn/college/1239/cfraction.html ",
                    "https://www.youzy.cn/college/2240/cfraction.html ",
                    "https://www.youzy.cn/college/1208/cfraction.html ",
                    "https://www.youzy.cn/college/1709/cfraction.html ",
                    "https://www.youzy.cn/college/1147/cfraction.html ",
                    "https://www.youzy.cn/college/2229/cfraction.html ",
                    "https://www.youzy.cn/college/937/cfraction.html ",
                    "https://www.youzy.cn/college/1072/cfraction.html ",
                    "https://www.youzy.cn/college/887/cfraction.html ",
                    "https://www.youzy.cn/college/1332/cfraction.html ",
                    "https://www.youzy.cn/college/1116/cfraction.html ",
                    "https://www.youzy.cn/college/998/cfraction.html ",
                    "https://www.youzy.cn/college/1879/cfraction.html ",
                    "https://www.youzy.cn/college/910/cfraction.html "
                ]
            },
            "op_setting": {
                "alias": "循环",
                "elemInIFrame": false,
                "iFrameXpath": "",
                "ifBreakAfterTime": false,
                "loopNum": 1,
                "loopWay": 4,
                "waitElem": "",
                "waitTime": 3
            },
            "op_type": 7,
            "singleElementlist": "",
            "sub_opList": [
                {
                    "op_param": {
                        "URL": "https://www.youzy.cn/college/1242/cfraction.html "
                    },
                    "op_setting": {
                        "CookieText": "BD_BRG_BID==={\"8005644\":\"d974a8ddd753bcb821eecad7\"}\nCNZZDATA1254568697===516148331-1542350535-%7C1542600575\nHMVT===12d15b68f4801f6d65dceb17ee817e26|1542605927|\nHm_lpvt_12d15b68f4801f6d65dceb17ee817e26===1542605922\nHm_lvt_12d15b68f4801f6d65dceb17ee817e26===1542355479,1542356045,1542357389,1542357645\nQIAO_CK_8005644_R===\nSERVER_ID===de45f6c7-2cb4728a\nUzy.AUTH===8341B0E43F38AC397BB2DA4C7A26A2AB18BFA34300B11C25713CF4AB4017C03B28B0929381904B308AF6B389659EE90B6E205731561F1574BE84316A9ABA009B536A0C542E5A32BC135E74EAA6B2725F91EB31ED5E655FE9A1B9DB276CFF0526E01A46BFF5B1238CF27344F37AE596A790E00843E740CB15F57A3E84E298B848\nYouzy.CurrentVersion===%7b%22Name%22%3a%22%e5%9b%9b%e5%b7%9d%22%2c%22EnName%22%3a%22sc%22%2c%22ProvinceId%22%3a855%2c%22Domain%22%3a%22http%3a%2f%2fsc.youzy.cn%22%2c%22Description%22%3a%22%22%2c%22QQGroup%22%3a%22125754301%22%2c%22QQGroupUrl%22%3anull%2c%22IsOpen%22%3atrue%2c%22Sort%22%3a11%2c%22Province%22%3a%7b%22Name%22%3a%22%e5%9b%9b%e5%b7%9d%22%2c%22Id%22%3a855%7d%2c%22Id%22%3a10%7d\nYouzy.FirstSelectVersion===1",
                        "alias": "打开网页",
                        "ifBlockAD": false,
                        "ifCleanCookie": false,
                        "ifLoop": true,
                        "ifMovepage": false,
                        "ifRedefCookie": true,
                        "ifRetryOpen": false,
                        "ifTextContain": "",
                        "ifTextNoContain": "",
                        "ifXpathContain": "",
                        "retryDelay": 5,
                        "retryTime": 5,
                        "timeout": 5,
                        "waitElem": "",
                        "waitTime": 3
                    },
                    "op_type": 1
                },
                {
                    "op_param": {
                    },
                    "op_setting": {
                        "alias": "判断条件",
                        "waitElem": "",
                        "waitTime": 2
                    },
                    "op_type": 8,
                    "sub_opList": [
                        {
                            "op_param": {
                                "condition": 2,
                                "elemXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/ul[1]/li[2]/a[1]",
                                "iFrameXpath": "\u0000",
                                "ifElemInIframe": false,
                                "text": ""
                            },
                            "op_setting": {
                                "alias": "条件分支",
                                "waitElem": "",
                                "waitTime": 3
                            },
                            "op_type": 9,
                            "sub_opList": [
                                {
                                    "fixedElementList": "",
                                    "op_param": {
                                        "param": ""
                                    },
                                    "op_setting": {
                                        "alias": "循环",
                                        "elemInIFrame": false,
                                        "iFrameXpath": "",
                                        "ifBreakAfterTime": false,
                                        "loopNum": 1,
                                        "loopWay": 3,
                                        "waitElem": "",
                                        "waitTime": 3
                                    },
                                    "op_type": 7,
                                    "singleElementlist": "",
                                    "sub_opList": [
                                        {
                                            "op_param": {
                                                "elemXpath": ""
                                            },
                                            "op_setting": {
                                                "AjaxLoad": false,
                                                "AjaxOverTime": 0,
                                                "AnchorId": "",
                                                "alias": "点击元素",
                                                "autoRetry": false,
                                                "ifLoop": true,
                                                "ifMovepage": false,
                                                "ifOpeninnewlabel": false,
                                                "ifRetryOpen": false,
                                                "locateAnchor": false,
                                                "retryDelay": 0,
                                                "retryTime": 1,
                                                "scrollTime": 0,
                                                "speedUp": false,
                                                "waitElem": "",
                                                "waitTime": 2
                                            },
                                            "op_type": 2
                                        },
                                        {
                                            "op_param": {
                                                "elem_list": [
                                                    {
                                                        "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/ul[1]/li[1]/a[1]",
                                                        "default": "hehe no data",
                                                        "name": "招生方向",
                                                        "relativeXPath": "",
                                                        "strategy": 0,
                                                        "useRelativeXpath": true,
                                                        "valueType": 1
                                                    }
                                                ]
                                            },
                                            "op_setting": {
                                                "alias": "提取数据",
                                                "ifLoop": true,
                                                "waitElem": "",
                                                "waitTime": 3
                                            },
                                            "op_type": 3
                                        },
                                        {
                                            "fixedElementList": "",
                                            "op_param": {
                                                "param": ""
                                            },
                                            "op_setting": {
                                                "alias": "循环",
                                                "elemInIFrame": false,
                                                "iFrameXpath": "",
                                                "ifBreakAfterTime": false,
                                                "loopNum": 1,
                                                "loopWay": 3,
                                                "waitElem": "",
                                                "waitTime": 3
                                            },
                                            "op_type": 7,
                                            "singleElementlist": "",
                                            "sub_opList": [
                                                {
                                                    "op_param": {
                                                        "elem_list": [
                                                            {
                                                                "absoluteXpath": "",
                                                                "default": "hehe no data",
                                                                "name": "年份",
                                                                "relativeXPath": "/td[1]",
                                                                "strategy": 0,
                                                                "useRelativeXpath": true,
                                                                "valueType": 1
                                                            },
                                                            {
                                                                "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[2]",
                                                                "default": "hehe no data",
                                                                "name": "批次",
                                                                "relativeXPath": "/td[2]",
                                                                "strategy": 0,
                                                                "useRelativeXpath": true,
                                                                "valueType": 1
                                                            },
                                                            {
                                                                "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[4]",
                                                                "default": "hehe no data",
                                                                "name": "最高分",
                                                                "relativeXPath": "/td[4]",
                                                                "strategy": 0,
                                                                "useRelativeXpath": true,
                                                                "valueType": 1
                                                            },
                                                            {
                                                                "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[5]",
                                                                "default": "hehe no data",
                                                                "name": "最低分",
                                                                "relativeXPath": "/td[5]",
                                                                "strategy": 0,
                                                                "useRelativeXpath": true,
                                                                "valueType": 1
                                                            },
                                                            {
                                                                "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[6]",
                                                                "default": "hehe no data",
                                                                "name": "平均分",
                                                                "relativeXPath": "/td[6]",
                                                                "strategy": 0,
                                                                "useRelativeXpath": true,
                                                                "valueType": 1
                                                            },
                                                            {
                                                                "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[7]",
                                                                "default": "hehe no data",
                                                                "name": "录取数",
                                                                "relativeXPath": "/td[7]",
                                                                "strategy": 0,
                                                                "useRelativeXpath": true,
                                                                "valueType": 1
                                                            },
                                                            {
                                                                "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[8]",
                                                                "default": "hehe no data",
                                                                "name": "最低为此",
                                                                "relativeXPath": "/td[8]",
                                                                "strategy": 0,
                                                                "useRelativeXpath": true,
                                                                "valueType": 1
                                                            },
                                                            {
                                                                "absoluteXpath": "/html/body/div[4]/div[1]/h2[1]",
                                                                "default": "hehe no data",
                                                                "name": "字段1",
                                                                "relativeXPath": "",
                                                                "strategy": 0,
                                                                "useRelativeXpath": false,
                                                                "valueType": 1
                                                            }
                                                        ]
                                                    },
                                                    "op_setting": {
                                                        "alias": "提取数据",
                                                        "ifLoop": true,
                                                        "waitElem": "",
                                                        "waitTime": 3
                                                    },
                                                    "op_type": 3
                                                }
                                            ],
                                            "textList": "",
                                            "unFixedElementList": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[position()>0]",
                                            "urlList": ""
                                        }
                                    ],
                                    "textList": "",
                                    "unFixedElementList": "/html/body/div[6]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/ul[1]/li[position()>0]/a[1]",
                                    "urlList": ""
                                }
                            ]
                        },
                        {
                            "op_param": {
                                "condition": 0,
                                "elemXpath": "",
                                "iFrameXpath": "\u0000",
                                "ifElemInIframe": false,
                                "text": ""
                            },
                            "op_setting": {
                                "alias": "条件分支",
                                "waitElem": "",
                                "waitTime": 0
                            },
                            "op_type": 9,
                            "sub_opList": [
                                {
                                    "fixedElementList": "",
                                    "op_param": {
                                        "param": ""
                                    },
                                    "op_setting": {
                                        "alias": "循环",
                                        "elemInIFrame": false,
                                        "iFrameXpath": "",
                                        "ifBreakAfterTime": false,
                                        "loopNum": 1,
                                        "loopWay": 3,
                                        "waitElem": "",
                                        "waitTime": 3
                                    },
                                    "op_type": 7,
                                    "singleElementlist": "",
                                    "sub_opList": [
                                        {
                                            "op_param": {
                                                "elem_list": [
                                                    {
                                                        "absoluteXpath": "",
                                                        "default": "hehe no data",
                                                        "name": "年份",
                                                        "relativeXPath": "/td[1]",
                                                        "strategy": 0,
                                                        "useRelativeXpath": true,
                                                        "valueType": 1
                                                    },
                                                    {
                                                        "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[2]",
                                                        "default": "hehe no data",
                                                        "name": "批次",
                                                        "relativeXPath": "/td[2]",
                                                        "strategy": 0,
                                                        "useRelativeXpath": true,
                                                        "valueType": 1
                                                    },
                                                    {
                                                        "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[4]",
                                                        "default": "hehe no data",
                                                        "name": "最高分",
                                                        "relativeXPath": "/td[4]",
                                                        "strategy": 0,
                                                        "useRelativeXpath": true,
                                                        "valueType": 1
                                                    },
                                                    {
                                                        "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[5]",
                                                        "default": "hehe no data",
                                                        "name": "最低分",
                                                        "relativeXPath": "/td[5]",
                                                        "strategy": 0,
                                                        "useRelativeXpath": true,
                                                        "valueType": 1
                                                    },
                                                    {
                                                        "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[6]",
                                                        "default": "hehe no data",
                                                        "name": "平均分",
                                                        "relativeXPath": "/td[6]",
                                                        "strategy": 0,
                                                        "useRelativeXpath": true,
                                                        "valueType": 1
                                                    },
                                                    {
                                                        "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[7]",
                                                        "default": "hehe no data",
                                                        "name": "录取数",
                                                        "relativeXPath": "/td[7]",
                                                        "strategy": 0,
                                                        "useRelativeXpath": true,
                                                        "valueType": 1
                                                    },
                                                    {
                                                        "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[8]",
                                                        "default": "hehe no data",
                                                        "name": "最低为此",
                                                        "relativeXPath": "/td[8]",
                                                        "strategy": 0,
                                                        "useRelativeXpath": true,
                                                        "valueType": 1
                                                    },
                                                    {
                                                        "absoluteXpath": "/html/body/div[6]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/ul[1]/li[1]/a[1]",
                                                        "default": "hehe no data",
                                                        "name": "招生方向",
                                                        "relativeXPath": "",
                                                        "strategy": 0,
                                                        "useRelativeXpath": false,
                                                        "valueType": 1
                                                    },
                                                    {
                                                        "absoluteXpath": "/html/body/div[4]/div[1]/h2[1]",
                                                        "default": "hehe no data",
                                                        "name": "大学名称",
                                                        "relativeXPath": "",
                                                        "strategy": 0,
                                                        "useRelativeXpath": false,
                                                        "valueType": 1
                                                    }
                                                ]
                                            },
                                            "op_setting": {
                                                "alias": "提取数据",
                                                "ifLoop": true,
                                                "waitElem": "",
                                                "waitTime": 3
                                            },
                                            "op_type": 3
                                        }
                                    ],
                                    "textList": "",
                                    "unFixedElementList": "/html/body/div[6]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[position()>0]",
                                    "urlList": ""
                                }
                            ]
                        }
                    ]
                }
            ],
            "textList": "",
            "unFixedElementList": "",
            "urlList": "https://www.youzy.cn/sc/\nhttps://www.youzy.cn/college/1242/cfraction.html \nhttps://www.youzy.cn/college/838/cfraction.html \nhttps://www.youzy.cn/college/1107/cfraction.html \nhttps://www.youzy.cn/college/848/cfraction.html \nhttps://www.youzy.cn/college/4248/cfraction.html \nhttps://www.youzy.cn/college/939/cfraction.html \nhttps://www.youzy.cn/college/926/cfraction.html \nhttps://www.youzy.cn/college/4130/cfraction.html \nhttps://www.youzy.cn/college/2981/cfraction.html \nhttps://www.youzy.cn/college/3708/cfraction.html \nhttps://www.youzy.cn/college/1983/cfraction.html \nhttps://www.youzy.cn/college/3449/cfraction.html \nhttps://www.youzy.cn/college/879/cfraction.html \nhttps://www.youzy.cn/college/1177/cfraction.html \nhttps://www.youzy.cn/college/839/cfraction.html \nhttps://www.youzy.cn/college/3980/cfraction.html \nhttps://www.youzy.cn/college/851/cfraction.html \nhttps://www.youzy.cn/college/1117/cfraction.html \nhttps://www.youzy.cn/college/857/cfraction.html \nhttps://www.youzy.cn/college/886/cfraction.html \nhttps://www.youzy.cn/college/854/cfraction.html \nhttps://www.youzy.cn/college/2985/cfraction.html \nhttps://www.youzy.cn/college/898/cfraction.html \nhttps://www.youzy.cn/college/4337/cfraction.html \nhttps://www.youzy.cn/college/922/cfraction.html \nhttps://www.youzy.cn/college/930/cfraction.html \nhttps://www.youzy.cn/college/1329/cfraction.html \nhttps://www.youzy.cn/college/1141/cfraction.html \nhttps://www.youzy.cn/college/843/cfraction.html \nhttps://www.youzy.cn/college/909/cfraction.html \nhttps://www.youzy.cn/college/1170/cfraction.html \nhttps://www.youzy.cn/college/1076/cfraction.html \nhttps://www.youzy.cn/college/852/cfraction.html \nhttps://www.youzy.cn/college/3209/cfraction.html \nhttps://www.youzy.cn/college/885/cfraction.html \nhttps://www.youzy.cn/college/835/cfraction.html \nhttps://www.youzy.cn/college/3369/cfraction.html \nhttps://www.youzy.cn/college/866/cfraction.html \nhttps://www.youzy.cn/college/916/cfraction.html \nhttps://www.youzy.cn/college/889/cfraction.html \nhttps://www.youzy.cn/college/3869/cfraction.html \nhttps://www.youzy.cn/college/2025/cfraction.html \nhttps://www.youzy.cn/college/908/cfraction.html \nhttps://www.youzy.cn/college/995/cfraction.html \nhttps://www.youzy.cn/college/840/cfraction.html \nhttps://www.youzy.cn/college/844/cfraction.html \nhttps://www.youzy.cn/college/873/cfraction.html \nhttps://www.youzy.cn/college/1035/cfraction.html \nhttps://www.youzy.cn/college/829/cfraction.html \nhttps://www.youzy.cn/college/847/cfraction.html \nhttps://www.youzy.cn/college/948/cfraction.html \nhttps://www.youzy.cn/college/918/cfraction.html \nhttps://www.youzy.cn/college/4193/cfraction.html \nhttps://www.youzy.cn/college/865/cfraction.html \nhttps://www.youzy.cn/college/1012/cfraction.html \nhttps://www.youzy.cn/college/971/cfraction.html \nhttps://www.youzy.cn/college/1482/cfraction.html \nhttps://www.youzy.cn/college/2490/cfraction.html \nhttps://www.youzy.cn/college/899/cfraction.html \nhttps://www.youzy.cn/college/896/cfraction.html \nhttps://www.youzy.cn/college/4171/cfraction.html \nhttps://www.youzy.cn/college/1139/cfraction.html \nhttps://www.youzy.cn/college/863/cfraction.html \nhttps://www.youzy.cn/college/858/cfraction.html \nhttps://www.youzy.cn/college/888/cfraction.html \nhttps://www.youzy.cn/college/830/cfraction.html \nhttps://www.youzy.cn/college/2293/cfraction.html \nhttps://www.youzy.cn/college/925/cfraction.html \nhttps://www.youzy.cn/college/1055/cfraction.html \nhttps://www.youzy.cn/college/1525/cfraction.html \nhttps://www.youzy.cn/college/934/cfraction.html \nhttps://www.youzy.cn/college/944/cfraction.html \nhttps://www.youzy.cn/college/1868/cfraction.html \nhttps://www.youzy.cn/college/877/cfraction.html \nhttps://www.youzy.cn/college/1143/cfraction.html \nhttps://www.youzy.cn/college/859/cfraction.html \nhttps://www.youzy.cn/college/3471/cfraction.html \nhttps://www.youzy.cn/college/834/cfraction.html \nhttps://www.youzy.cn/college/3420/cfraction.html \nhttps://www.youzy.cn/college/3472/cfraction.html \nhttps://www.youzy.cn/college/955/cfraction.html \nhttps://www.youzy.cn/college/1703/cfraction.html \nhttps://www.youzy.cn/college/963/cfraction.html \nhttps://www.youzy.cn/college/902/cfraction.html \nhttps://www.youzy.cn/college/904/cfraction.html \nhttps://www.youzy.cn/college/954/cfraction.html \nhttps://www.youzy.cn/college/929/cfraction.html \nhttps://www.youzy.cn/college/878/cfraction.html \nhttps://www.youzy.cn/college/947/cfraction.html \nhttps://www.youzy.cn/college/1289/cfraction.html \nhttps://www.youzy.cn/college/1010/cfraction.html \nhttps://www.youzy.cn/college/872/cfraction.html \nhttps://www.youzy.cn/college/3450/cfraction.html \nhttps://www.youzy.cn/college/974/cfraction.html \nhttps://www.youzy.cn/college/1008/cfraction.html \nhttps://www.youzy.cn/college/2493/cfraction.html \nhttps://www.youzy.cn/college/3241/cfraction.html \nhttps://www.youzy.cn/college/864/cfraction.html \nhttps://www.youzy.cn/college/917/cfraction.html \nhttps://www.youzy.cn/college/1570/cfraction.html \nhttps://www.youzy.cn/college/1689/cfraction.html \nhttps://www.youzy.cn/college/2074/cfraction.html \nhttps://www.youzy.cn/college/1202/cfraction.html \nhttps://www.youzy.cn/college/1300/cfraction.html \nhttps://www.youzy.cn/college/1044/cfraction.html \nhttps://www.youzy.cn/college/1491/cfraction.html \nhttps://www.youzy.cn/college/855/cfraction.html \nhttps://www.youzy.cn/college/1045/cfraction.html \nhttps://www.youzy.cn/college/1263/cfraction.html \nhttps://www.youzy.cn/college/3412/cfraction.html \nhttps://www.youzy.cn/college/1558/cfraction.html \nhttps://www.youzy.cn/college/3217/cfraction.html \nhttps://www.youzy.cn/college/1719/cfraction.html \nhttps://www.youzy.cn/college/1511/cfraction.html \nhttps://www.youzy.cn/college/2322/cfraction.html \nhttps://www.youzy.cn/college/3960/cfraction.html \nhttps://www.youzy.cn/college/3476/cfraction.html \nhttps://www.youzy.cn/college/1656/cfraction.html \nhttps://www.youzy.cn/college/893/cfraction.html \nhttps://www.youzy.cn/college/3959/cfraction.html \nhttps://www.youzy.cn/college/1060/cfraction.html \nhttps://www.youzy.cn/college/1775/cfraction.html \nhttps://www.youzy.cn/college/1361/cfraction.html \nhttps://www.youzy.cn/college/1417/cfraction.html \nhttps://www.youzy.cn/college/2164/cfraction.html \nhttps://www.youzy.cn/college/905/cfraction.html \nhttps://www.youzy.cn/college/1175/cfraction.html \nhttps://www.youzy.cn/college/958/cfraction.html \nhttps://www.youzy.cn/college/928/cfraction.html \nhttps://www.youzy.cn/college/1003/cfraction.html \nhttps://www.youzy.cn/college/1527/cfraction.html \nhttps://www.youzy.cn/college/3253/cfraction.html \nhttps://www.youzy.cn/college/1130/cfraction.html \nhttps://www.youzy.cn/college/932/cfraction.html \nhttps://www.youzy.cn/college/915/cfraction.html \nhttps://www.youzy.cn/college/2506/cfraction.html \nhttps://www.youzy.cn/college/3445/cfraction.html \nhttps://www.youzy.cn/college/1127/cfraction.html \nhttps://www.youzy.cn/college/849/cfraction.html \nhttps://www.youzy.cn/college/1862/cfraction.html \nhttps://www.youzy.cn/college/1708/cfraction.html \nhttps://www.youzy.cn/college/832/cfraction.html \nhttps://www.youzy.cn/college/3661/cfraction.html \nhttps://www.youzy.cn/college/2983/cfraction.html \nhttps://www.youzy.cn/college/1178/cfraction.html \nhttps://www.youzy.cn/college/1182/cfraction.html \nhttps://www.youzy.cn/college/1234/cfraction.html \nhttps://www.youzy.cn/college/4197/cfraction.html \nhttps://www.youzy.cn/college/936/cfraction.html \nhttps://www.youzy.cn/college/1360/cfraction.html \nhttps://www.youzy.cn/college/964/cfraction.html \nhttps://www.youzy.cn/college/1199/cfraction.html \nhttps://www.youzy.cn/college/979/cfraction.html \nhttps://www.youzy.cn/college/1969/cfraction.html \nhttps://www.youzy.cn/college/846/cfraction.html \nhttps://www.youzy.cn/college/1439/cfraction.html \nhttps://www.youzy.cn/college/975/cfraction.html \nhttps://www.youzy.cn/college/3250/cfraction.html \nhttps://www.youzy.cn/college/1106/cfraction.html \nhttps://www.youzy.cn/college/2081/cfraction.html \nhttps://www.youzy.cn/college/1088/cfraction.html \nhttps://www.youzy.cn/college/2551/cfraction.html \nhttps://www.youzy.cn/college/837/cfraction.html \nhttps://www.youzy.cn/college/1021/cfraction.html \nhttps://www.youzy.cn/college/827/cfraction.html \nhttps://www.youzy.cn/college/1232/cfraction.html \nhttps://www.youzy.cn/college/1168/cfraction.html \nhttps://www.youzy.cn/college/4102/cfraction.html \nhttps://www.youzy.cn/college/1706/cfraction.html \nhttps://www.youzy.cn/college/941/cfraction.html \nhttps://www.youzy.cn/college/870/cfraction.html \nhttps://www.youzy.cn/college/1998/cfraction.html \nhttps://www.youzy.cn/college/3354/cfraction.html \nhttps://www.youzy.cn/college/3975/cfraction.html \nhttps://www.youzy.cn/college/1245/cfraction.html \nhttps://www.youzy.cn/college/2367/cfraction.html \nhttps://www.youzy.cn/college/3422/cfraction.html \nhttps://www.youzy.cn/college/1249/cfraction.html \nhttps://www.youzy.cn/college/1354/cfraction.html \nhttps://www.youzy.cn/college/3979/cfraction.html \nhttps://www.youzy.cn/college/1054/cfraction.html \nhttps://www.youzy.cn/college/1087/cfraction.html \nhttps://www.youzy.cn/college/1069/cfraction.html \nhttps://www.youzy.cn/college/2491/cfraction.html \nhttps://www.youzy.cn/college/1184/cfraction.html \nhttps://www.youzy.cn/college/2397/cfraction.html \nhttps://www.youzy.cn/college/1090/cfraction.html \nhttps://www.youzy.cn/college/1693/cfraction.html \nhttps://www.youzy.cn/college/1975/cfraction.html \nhttps://www.youzy.cn/college/2947/cfraction.html \nhttps://www.youzy.cn/college/1970/cfraction.html \nhttps://www.youzy.cn/college/1026/cfraction.html \nhttps://www.youzy.cn/college/1239/cfraction.html \nhttps://www.youzy.cn/college/2240/cfraction.html \nhttps://www.youzy.cn/college/1208/cfraction.html \nhttps://www.youzy.cn/college/1709/cfraction.html \nhttps://www.youzy.cn/college/1147/cfraction.html \nhttps://www.youzy.cn/college/2229/cfraction.html \nhttps://www.youzy.cn/college/937/cfraction.html \nhttps://www.youzy.cn/college/1072/cfraction.html \nhttps://www.youzy.cn/college/887/cfraction.html \nhttps://www.youzy.cn/college/1332/cfraction.html \nhttps://www.youzy.cn/college/1116/cfraction.html \nhttps://www.youzy.cn/college/998/cfraction.html \nhttps://www.youzy.cn/college/1879/cfraction.html \nhttps://www.youzy.cn/college/910/cfraction.html "
        }
    ],
    "title": "优志愿招生历史数据测试任务"
}

    
    
    '''

    taskDesc1 = "{\"opList\":[{\"op_setting\":{\"ifRetry\":false,\"ifBlockAD\":false,\"retryTime\":5,\"ifRedefCookie\":false,\"ifMovepage\":false,\"timeout\":5,\"ifLoop\":false,\"ifCleanCookie\":false,\"retryDelay\":5,\"ifTextNoContain\":\"\",\"CookieText\":\"\",\"alias\":\"\xe6\x89\x93\xe5\xbc\x80\xe7\xbd\x91\xe9\xa1\xb5\",\"waitElem\":\"\",\"waitTime\":3,\"ifTextContain\":\"\",\"ifXpathContain\":\"\"},\"op_type\":1,\"op_param\":{\"URL\":\"http://www.baidu.com\"}},{\"op_setting\":{\"alias\":\"\xe6\x8f\x90\xe5\x8f\x96\xe6\x95\xb0\xe6\x8d\xae\",\"waitElem\":\"\",\"waitTime\":3},\"op_type\":3,\"op_param\":{\"elem_list\":[{\"default\":\"hehe no data\",\"valueType\":\"1\",\"name\":\"\xe5\xad\x97\xe6\xae\xb51\",\"strategy\":0,\"elemXpath\":\"\"},{\"default\":\"hehe no data\",\"valueType\":\"1\",\"name\":\"\xe5\xad\x97\xe6\xae\xb52\",\"strategy\":0,\"elemXpath\":\"\"},{\"default\":\"hehe no data\",\"valueType\":\"1\",\"name\":\"\xe5\xad\x97\xe6\xae\xb53\",\"strategy\":0,\"elemXpath\":\"\"}]}}],\"title\":\"\xe4\xba\x91\xe6\xb5\x8b\xe8\xaf\x95\"}"

    # json_task = json.loads(taskDesc1, object_pairs_hook=OrderedDict, strict=False)  # strict 设为False,允许字符串里有转意字符
    # op_list = json_task['opList']
    # event = Event(Execute(),9,99)
    # for op in op_list:
    #     op_type = op['op_type']
    #     if op_type == 1:
    #         event.open_web(op)
    #     elif op_type == 2:
    #         event.click(op)
    #     elif op_type == 3:
    #         event.extract_data(op)
    #     elif op_type == 4:
    #         event.input_text(op)
    #     elif op_type ==7:
    #         event.loop(op)