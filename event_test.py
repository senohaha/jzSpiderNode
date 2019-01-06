# -*- coding: utf-8 -*-
from selenium import webdriver
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
from threading import Thread

SlaveId = 1


class Event(object):
    def __init__(self, userId, taskId):
        self.driver = webdriver.Firefox()
        self.wait = WebDriverWait(self.driver, 10)

        self.server = pymongo.MongoClient()
        self.db = self.server['spider_data']  # 库

        collection = '{userId}_{taskId}'.format(userId=userId, taskId=taskId)

        self.db = self.db[collection]  # 集合

    # 1 打开网页  参数的URL,代表循环上的url
    def open_web(self, jsondata, url=None):
        dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        op_settings_dict = dictdata['op_settings']
        timeout = op_settings_dict.get('timeout', default=5)
        ifBlockAD = op_settings_dict.get('ifBlockAD', default=True)

        ifLoop = op_settings_dict.get('ifLoop', default=False)
        # 如果不使用当前所在循环给的url循环，就用自己的
        if ifLoop is False:
            url = dictdata['op_param']['URL']
        if url is None:
            print '请输入一个链接'

        ifMovepage = op_settings_dict.get('ifMovepage', default=False)
        if ifMovepage is True:
            # 解析出滚动网页的参数
            movepageConf = op_settings_dict['movepageConf']
            moveSum = movepageConf['moveSum']
            moveSpace = movepageConf['moveSpace']
            moveDir = movepageConf['moveDir']

        ifCleanCookie = op_settings_dict.get('ifCleanCookie', default=False)
        ifRedefCookie = op_settings_dict.get('ifRedefCookie', default=False)
        if ifRedefCookie is True:  # 使用用户自定义的cookie
            redefCookieValue = op_settings_dict.get('redefCookieValue', default=None)
        ifRetryOpen = op_settings_dict.get('ifRetryOpen', default=False)

        self.driver.get(url)

    # 2 点击事件  参数elemXpath是循环传来的
    def click(self, jsondata, elemXpath=None):
        dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        op_settings_dict = dictdata['op_setting']
        # 执行该动作前 等待参数
        waitConf_dict = op_settings_dict['waitConf']
        waitTime = waitConf_dict['waitTime']
        waitElem = waitConf_dict['waitElem']
        # 是否点击当前循环中设置的元素 ？ 默认不使用
        print op_settings_dict, 'dict'
        ifLoop = op_settings_dict.get('ifLoop', False)
        # 是否在新标签中打开网页
        ifOpeninnewlabel = op_settings_dict['ifOpeninnewlabel']
        # 是否加载完页面后滚动网页 及 参数
        ifMovepage = op_settings_dict['ifMovepage']

        if ifLoop is False:
            # 点击元素的xpath
            elemXpath = dictdata['op_param']['elemXpath']

        # 是否重试点击元素
        ifRetryClick = op_settings_dict['ifRetryClick']

        # 点击元素前等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem is not None:
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '点击元素前，等待超时'
        # 在新页面打开？
        if ifOpeninnewlabel:
            pass
        # 滚动页面
        if ifMovepage:
            movePageconf = op_settings_dict['movePageconf']
            moveSum = movePageconf['moveSum']
            moveSpace = movePageconf['moveSpace']
            moveDir = movePageconf['moveDir']
            for i in range(moveSum):
                js = "document.documentElement.scrollTop=" + str(1000 * (i + 1)) + ""
                self.driver.execute_script(js)
                time.sleep(moveSpace)
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
        dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)

        op_settings_dict = dictdata['op_setting']
        # 执行该动作前 等待参数
        waitConf_dict = op_settings_dict['waitConf']
        waitTime = waitConf_dict['waitTime']
        waitElem = waitConf_dict['waitElem']
        # 等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem is not None:
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '提取数据前，等待超时'

        # 是否点击当前循环中设置的元素 ？
        ifLoop = op_settings_dict['ifLoop']

        op_param_dict = dictdata['op_param']
        # 需要提取的所有字段
        elem_list = op_param_dict['elem_list']
        # 用于存提取的文档item = {'学校':'山东大学','代码':'123456','地址':'aaaaa'}
        item = {}
        for elem in elem_list:
            # 每个字段的参数
            elem_dict = elem['elem']
            name = elem_dict['name']
            elemXpath = elem_dict['elemXpath']
            # 对本动作在循环中做处理  , 有的字段可能在当前循环下，有的不在
            if loop_xpath is not None:
                # '/html/ul/li[position()>0]' ->'/html/ul'
                list = loop_xpath.split('/')
                pop = list.pop()
                pre_loop_xapth = '/'.join(list)
                # elemXpath = '/html/ul/li[position()>0]/div/div[3]/a/em' ->'/html/ul/li[position()=count]/div/div[3]/a/em'

                if pre_loop_xapth in elemXpath:  # 如果该字段的xpath在循环中
                    position = ''
                    for i in pop:
                        if i is not '[':
                            position += i
                        else:
                            break
                    temp = '[position()=%s]' % count
                    position += temp
                    elemXpath_pre = pre_loop_xapth + '/' + position  # /html/ul/li[position()=count]
                    aa = elemXpath[len(pre_loop_xapth):].split('/')
                    aa.pop(0)
                    aa.pop(0)
                    elemXpath_suf = '/'.join(aa)
                    elemXpath = elemXpath_pre + '/' + elemXpath_suf

                    # 不在循环的不做处理

            valueType = elem_dict['valueType']
            unfind_dict = elem_dict['unfind']
            ifSetNull = unfind_dict['ifSetNull']
            ifSetAllNull = unfind_dict['ifSetAllNull']
            useDefault = unfind_dict['useDefault']
            try:
                # 等待此xpath的出现
                WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, elemXpath)))
                # 出现后爬取
                if valueType == 1:  # 文本
                    print elemXpath, 'lllll'
                    item[name] = self.driver.find_element(By.XPATH, elemXpath).text
                elif valueType == 2:  # 链接
                    print elemXpath, 'hahah'
                    href = self.driver.find_element(By.XPATH, elemXpath).get_attribute('href')
                    src = self.driver.find_element(By.XPATH, elemXpath).get_attribute('src')
                    if href is not None:
                        item[name] = href
                    else:
                        item[name] = src
                elif valueType == 3:  # 或取当前网页标题
                    item[name] = self.driver.title

            except TimeoutException as e:
                # 找不到该字段的处理方式
                if ifSetNull:
                    item[name] = None
                elif useDefault is not None:
                    item[name] = useDefault
        print item
        # self.db.insert(item)

    # 4 输入文本
    def input_text(self, jsondata):
        dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        op_settings_dict = dictdata['op_settings']
        # 执行该动作前 等待参数
        waitConf_dict = op_settings_dict['waitConf']
        waitTime = waitConf_dict['waitTime']
        waitElem = waitConf_dict['waitele']
        # 等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem is not None:
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
    def loop(self, jsondata):
        dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        op_settings_dict = dictdata['op_settings']
        # 执行该动作前 等待参数
        waitConf_dict = op_settings_dict['waitConf']
        waitTime = waitConf_dict['waitTime']
        waitElem = waitConf_dict['waitele']
        # 循环终止次数
        loopNum = op_settings_dict['loopNum']
        # 循环方式
        loopWay = op_settings_dict['loopWay']
        # 根据 不同的循环方式 得到 循环参数 param_list
        op_param_dict = dictdata['op_param']

        param_list = []
        elemXpath = None
        if loopWay == 1:  # 单个元素(循环点击下一页)
            elemXpath = op_param_dict['elemXpath']
        elif loopWay == 2:  # 固定元素列表  点击链接
            elemXpath = op_param_dict['elemXpath']
            param_list = self.driver.find_elements_by_xpath(elemXpath)
        elif loopWay == 3:  # 不固定元素列表   elemXpath 为外循环,如‘/html/div/div([position>0])’
            elemXpath = op_param_dict['elemXpath']
            param_list = self.driver.find_elements_by_xpath(elemXpath)

        elif loopWay == 4:  # url列表
            param_list = op_param_dict['param_list']
        elif loopWay == 5:  # 文本列表
            param_list = op_param_dict['param_list']
        else:
            print '循环方式出错'

        sub_opList = dictdata['sub_opList']

        if loopWay == 1:  # 循环点击单个元素
            pass
        else:  # 依据列表循环
            count = 0
            for i in param_list:  # 依据循环参数循环！！！！
                count = count + 1
                # 每次循环的子动作
                for op_node in sub_opList:
                    # op_nodes_dict = json.loads(op_nodes, object_pairs_hook=OrderedDict)
                    # op_node = op_nodes_dict['op_node']
                    op_node_dict = json.loads(op_node, object_pairs_hook=OrderedDict)
                    op_type = op_node_dict['op_type']
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

    # 8 判断条件
    def condition(self, jsondata):
        dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        op_settings_dict = dictdata['op_settings']
        # 执行该动作前 等待参数
        waitConf_dict = op_settings_dict['waitConf']
        waitTime = waitConf_dict['waitTime']
        waitElem = waitConf_dict['waitele']
        # 等待
        if waitTime is not 0:
            time.sleep(waitTime)
        if waitElem is not None:
            try:
                WebDriverWait(self.driver, waitTime, 0.5).until(EC.presence_of_element_located((By.XPATH, waitElem)))
            except TimeoutException as e:
                print '判断条件，等待超时'

        sub_opList = dictdata['sub_opList']
        for op_nodes in sub_opList:
            op_node = op_nodes['op_node']
            op_type = op_node['op_type']
            if op_type != 9:
                print '判断条件的子动作必须是条件分支'
                continue
                # ??????????????????

    # 9 条件分支
    def branch(self, jsondata):
        dictdata = json.loads(jsondata, object_pairs_hook=OrderedDict)
        op_settings_dict = dictdata['op_settings']
        # 执行该动作前 等待参数
        waitConf_dict = op_settings_dict['waitConf']
        waitTime = waitConf_dict['waitTime']
        # 等待
        if waitTime is not 0:
            time.sleep(waitTime)
        op_param_dict = dictdata['op_param']
        # 以下三个条件只能选一个，作为本分支执行的条件
        ifTextContain = op_param_dict.get('ifTextContain', default=None)
        ifElemContain = op_param_dict.get('ifElemContain', default=None)
        ifAlways = op_param_dict.get('ifAlways', default=None)
        if ifTextContain is not None:
            page_source = self.driver.page_source
            if ifTextContain.decode('utf-8') not in page_source:
                return
        elif ifElemContain is not None:
            try:
                self.driver.find_element_by_xpath(ifElemContain)
            except Exception:
                return
        elif ifAlways is not None:
            if ifAlways is False:
                return

        # 条件满足执行该分支(子动作列表)
        sub_opList = dictdata['sub_opList']

        # 解析子动作
        self.parse_opList(sub_opList)

    # 解析子动作
    def parse_opList(self, sub_opList):
        for op_nodes in sub_opList:
            op_nodes_dict = json.loads(op_nodes, object_pairs_hook=OrderedDict)
            op_node = op_nodes_dict['op_node']
            op_node_dict = json.loads(op_node, object_pairs_hook=OrderedDict)
            op_type = op_node_dict['op_type']
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






















class Execute():
    def __init__(self):
        self.redis_conn = redis.Redis()

    def execute(self, userId, taskId):
        # 轮询redis该用户该任务的子任务队列‘task:{userId}:{taskId}:urllist’
        pid = os.getpid()   # ?与protocol一致否？？？？？

        taskDescKey = 'task:{userId}:{taskId}:desc'.format(userId=userId, taskId=taskId)
        urllistkey = 'task:{userId}:{taskId}:urllist'.format(userId=userId, taskId=taskId)
        processLiveKey = 'process:{slaveId}:{userId}:{taskId}:{pid}'. \
            format(slaveId=SlaveId, userId=userId, taskId=taskId, pid=pid)
        while True:
            if self.redis_conn.get(processLiveKey) == 'stop':
                break
            if self.redis_conn.llen(urllistkey) == 0:
                break
            url = self.redis_conn.lpop(urllistkey)
            taskDesc = self.redis_conn.hget(taskDescKey, 'taskDescription')

            self.event = Event(userId, taskId)





if __name__ == "__main__":
    userId = sys.argv[1]
    taskId = sys.argv[2]

    Execute().execute('1', '1')
    # Execute().execute(userId, taskId)