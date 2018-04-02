#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "husterxsp"

import io
import json
import sys
import time
import requests
import re
from bs4 import BeautifulSoup

# reload(sys)
# sys.setdefaultencoding("utf-8")

result = {}
def main():
    global result
    main_url = "http://jwjz.ucas.ac.cn/jiaowu/classroom/allclassroomforquery.asp"

    headers = {
        'Cookie': 'ASPSESSIONIDASSCSTCD=HMFDNLPDGBLCIIBAFAHPADLO; ASPSESSIONIDCQSDSSCD=EFLBIJJAELAJCMEKCIGBFDHC',
        'user-agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }

    time_secs = time.mktime(time.strptime('2018-03-05', "%Y-%m-%d"))
    for week in range(1, 23):
        for weekday in range(1, 8):

            time_tuple = time.localtime(time_secs)
            # 2018 春季学期 03.05 开学 
            # 周，星期，校区
            # 周一 ~ 周日：001 ~ 111
            # yq: 3 雁栖湖校区
            # 本学期 22 周
            parma = {
                'weekname': week,
                'weekday_name': toBin(weekday),
                'yq': 3
            }

            result = {
                'weekname': week,
                'weekday_name': weekday,
                'room_data': []
            }

            print('start: week' + str(week) + ' weekday' + str(weekday))
            # 编码问题。。。深坑
            # 先print 查看 response 编码是否正确。再看soup编码是否正确。
            response = requests.post(main_url, headers = headers, data = parma)            
            content = response.content.decode('gb18030')

            parse(time_tuple, content)
            time_secs += 24 * 60 * 60


def parse(time_tuple, content):
    soup = BeautifulSoup(content, 'html.parser')    
    table_list = soup.find_all("table")
    table = table_list[9]

    tr_list = table.find_all('tr', recursive = False)
    del tr_list[0]

    for tr_item in tr_list:
        td_list = tr_item.find_all('td', recursive = False)

        room = td_list[0].text
        study = []

        for i in range(1, 13):
            if len(td_list[i].find_all('img')) == 0:
                study.append(i)

        result['room_data'].append({
            'room': room,
            'available': study
        })

    # https://stackoverflow.com/questions/36003023/json-dump-failing-with-must-be-unicode-not-str-typeerror/36003774
    output = io.open("data/%s-%s-%s.json"%(str(time_tuple.tm_year), str(time_tuple.tm_mon), str(time_tuple.tm_mday)), 'w', encoding="utf-8")
    output.write(unicode(json.dumps(result, ensure_ascii = False)))
    output.close

def toBin(num):
    num = bin(num)
    num = re.search('0b(\d+)', num).group(1)
    while len(num) < 3:
        num = '0' + num
    return num

if __name__ == '__main__':
    main()
