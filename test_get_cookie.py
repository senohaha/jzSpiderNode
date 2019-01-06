import time
from selenium import webdriver
if __name__=='__main__':
    CookieText = 'JSESSIONID===C3813B1EC97ACD27785FDE66606FB885\n_site_id_cookie===1\nadSwitch===true\nbatchLineYear===2018\nclientlanguage===zh_CN\ncollegeHistoryYear===2017\ndiscount===5\nhistoryYear===2017\nisLimit===true\nloginTye===5\noneparagraphYear===2018\nplanYear===2018\nportal===1\nsuperMember===\nuser_city===%E6%88%90%E9%83%BD%E5%B8%82\nuser_province===%E5%9B%9B%E5%B7%9D\nuser_rank===9225\nuser_score===633\nuser_subject===%E7%90%86%E7%A7%91\nusername===18011472186'
    driver = webdriver.Firefox()
    driver.get('http://192.168.20.11:8080')
    print 'kkkk'
    cookie_list = CookieText.split('\n')
    for cookie_str in cookie_list:
        k_v = cookie_str.split('===')
        key = k_v[0]
        value = k_v[1]
        print key, ':', value
        driver.add_cookie({'name': key, 'value': value})

    print 'lll'
    driver.get('http://192.168.20.11:8080')
    print 'aaaa'

    # driver = webdriver.Firefox()
    # driver.get('http://192.168.20.11:8080')
    # driver.delete_all_cookies()
    # driver.add_cookie({'name': '_site_id_cookie', 'value': '1'})
    # driver.add_cookie({'name': 'adSwitch', 'value': 'true'})
    # driver.add_cookie({'name': 'batchLineYear', 'value': '2018'})
    # driver.add_cookie({'name': 'clientlanguage', 'value': 'zh_CN'})
    # driver.add_cookie({'name': 'collegeHistoryYear', 'value': '2017'})
    # driver.add_cookie({'name': 'discount', 'value': '5'})
    # driver.add_cookie({'name': 'historyYear', 'value': '2017'})
    # driver.add_cookie({'name': 'isLimit', 'value': 'true'})
    # driver.add_cookie({'name': 'loginTye', 'value': '5'})
    # driver.add_cookie({'name': 'oneparagraphYear', 'value': '2018'})
    # driver.add_cookie({'name': 'planYear', 'value': '2018'})
    # driver.add_cookie({'name': 'portal', 'value': '1'})
    # driver.add_cookie({'name': 'superMember', 'value': ''})
    # print 'll'
    # driver.get('http://192.168.20.11:8080')
    # print 'kk'





    # driver = webdriver.Firefox()
    # driver.get('https://www.qq.com/')
    # driver.add_cookie({'name': 'RK', 'value': '0MU6eq1rGb'})
    # driver.add_cookie({'name': 'pac_uid', 'value': '1_416158460'})
    # driver.add_cookie({'name': 'ptcz', 'value': '1fbe7ccae2af4135574952043b6db2d8a04dbdd2935ae19824728460fbffc08f'})
    # driver.add_cookie({'name': 'ad_play_index', 'value': '85'})
    # driver.add_cookie({'name': 'ptui_loginuin', 'value': '416158460'})
    # driver.add_cookie({'name': 'o_cookie', 'value': '945092316'})
    # driver.add_cookie({'name': 'fp3_id1', 'value': '1100263323A68BFC2488AD48C84ABED9E313B675F5B2316337B349E3FDE3001AC58295E532FFECF07F2F86B1999047E2592A'})
    # driver.add_cookie({'name': 'ts_uid', 'value': '1313032092'})
    # driver.add_cookie({'name': 'pgv_pvid', 'value': '1918975328'})
    # driver.add_cookie({'name': 'pgv_pvi', 'value': '8087061504'})
    # driver.add_cookie({'name': 'skey', 'value': '@Uz84lI6v2'})
    # driver.add_cookie({'name': 'ptisp', 'value': 'ctc'})
    # driver.add_cookie({'name': 'pt2gguin', 'value': 'o0416158460'})
    # driver.add_cookie({'name': 'uin', 'value': 'o0416158460'})
    # driver.add_cookie({'name': 'qm_lg', 'value': 'qm_lg'})
    # driver.add_cookie({'name': 'pgv_si', 'value': 's7232643072'})
    # driver.add_cookie({'name': 'pgv_info', 'value': 'ssid=s3896346935'})
    # driver.add_cookie({'name': 'ts_refer', 'value': 'www.baidu.com/link'})
    # driver.add_cookie({'name': 'ts_last', 'value': 'www.qq.com/'})





    # driver.get('https://www.youzy.cn/college/838/newplan.html')
    # driver.delete_all_cookies()
    # driver.add_cookie({'name': 'Hm_lvt_12d15b68f4801f6d65dceb17ee817e26', 'value': '1537250853,1539154558'})
    # driver.add_cookie({'name': 'UM_distinctid', 'value': '164cc6512c220d-00530301af5016-386a4645-13c680-164cc6512c3115'})
    # driver.add_cookie({'name': 'Uzy.AUTH', 'value': '58F0AD8AEBA321A93BCB151E40A0B4E85B4DF0EC23EB2F55ECD776847F1A411B10AE98111955462AB9D9FC85F38C1BA050756787A0BE61726F890D9B95E6B9DEC1058976D068C304851A9A93710D1F94FC7E8508D0836D5E12948FA439B652A479BCA26425307D5EE19FB2F93DF114D11D0B2A40BBC21E764216A2B0518165BD'})
    # driver.add_cookie({'name': 'CNZZDATA1254568697', 'value': '1583100496-1532434586-%7C1539149838'})
    # driver.add_cookie({'name': 'QIAO_CK_8005644_R', 'value': ''})
    # driver.add_cookie({'name': 'SERVER_ID', 'value': '1'})
    # driver.add_cookie({'name': 'Hm', 'value': '1beb241f-26c392ec'})
    # a = str(int(time.time()))
    # print a
    # driver.add_cookie({'name': 'Hm_lpvt_12d15b68f4801f6d65dceb17ee817e26', 'value': a})


    # driver.get('https://www.qq.com/')