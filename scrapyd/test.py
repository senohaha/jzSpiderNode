# -*- coding: utf-8 -*-
from selenium import webdriver

# test    爬取 success
# json_1 = '{"op_type": 3,"op_setting":{"alias":"提取数据","waitConf":{"waitTime":0,"waitElem":null},' \
#          '"ifLoop":true},"op_param":{"elem_list":[' \
#          '{"elem":{"name":"价钱","elemXpath":"/html/body/div[1]/div[2]/div[3]/div[1]/div[21]/div/div/div[1]/div[1]/div[2]/div[1]/div[1]/strong",' \
#          '"valueType": 1, "unfind":{"ifSetNull":true,"ifSetAllNull":false,"useDefault":null}}},' \
#          '{"elem":{"name":"出版商","elemXpath":"/html/body/div[1]/div[2]/div[3]/div[1]/div[21]/div/div/div[1]/div[1]/div[2]/div[3]/div[1]/a/span[2]","valueType": 1, ' \
#          '"unfind":{"ifSetNull":true,"ifSetAllNull":false,"useDefault":null}}}]},"sub_opList":[]}'
# a = Event('q', 'd')
# a.driver.get(
#     'https://s.taobao.com/search?q=python&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20180828&ie=utf8')
# waixpath = '/html/body/div[1]/div[2]/div[3]/div[1]/div[21]/div/div/div[1]/div[1]'
# a.extract_data(json_1, count=1, loop_xpath=waixpath)


if __name__=='__main__':
    driver = webdriver.Firefox()
    # driver.get('https://s.taobao.com/search?q=python&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20180828&ie=utf8')
    # a = driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div[3]/div[1]/div[21]/div/div/div[1]/div')
    # print a
    driver.get('https://s.taobao.com/search?q=python&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20180828&ie=utf8')
    waixpath = '/html/body/div[1]/div[2]/div[3]/div[1]/div[21]/div/div/div[1]/div[position()>0]/div[2]/div[2]/a'
    lis = driver.find_elements_by_xpath(waixpath)


