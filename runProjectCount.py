# -*- coding: utf-8 -*-
# -------------------------------------
# @Time    : 2022/5/16 15:38
# @Author  : Luobo
# @Email   : 1986494745@qq.com
# @File    : runProjectCount.py
# @Software: PyCharm
# @Describe: 统计Tb上项目的缺陷数量
# -------------------------------------


import requests
import json
import time
import base64
import hashlib
import hmac
import re

# 参数化配置 需要更新为自己的userCookie
parameters: dict = {
    # 筛选时间 本周
    'filterWeek': "startOf(w)&endOf(w)",
    # 筛选时间 上周
    # 'filterWeek': "startOf(w, -1w)&endOf(w, -1w)"
    'userCookie': 'teambition_lang=zh; referral=%7B%22domain%22%3A%22www.teambition.com%22%2C%22path%22%3A%22%2F%22%2C%22query%22%3A%22%22%2C%22hash%22%3A%22%22%7D; _ga=GA1.2.1972011967.1652085209; TEAMBITION_SESSIONID=eyJhdXRoVXBkYXRlZCI6MTU5MTYwODk2OTIwMSwibG9naW5Gcm9tIjoiZGluZ1RhbGsiLCJzdGF0ZSI6e30sInVpZCI6IjVlY2I0OTJhMWZhMzMxMWJlMjgwOTAwZCIsInVzZXIiOnsiX2lkIjoiNWVjYjQ5MmExZmEzMzExYmUyODA5MDBkIiwibmFtZSI6IuaYn+eBqyIsImVtYWlsIjoieGluZ2h1b0B5c2NyZWRpdC5jb20iLCJhdmF0YXJVcmwiOiJodHRwczovL3Rjcy50ZWFtYml0aW9uLm5ldC90aHVtYm5haWwvMTExdGU1MmE0OWFiNzU5NmM2Yzg0NmQzNDAzZjAzMDE2ZGEzL3cvMTAwL2gvMTAwIiwicmVnaW9uIjoiY24iLCJsYW5nIjoiIiwiaXNSb2JvdCI6ZmFsc2UsIm9wZW5JZCI6IiIsInBob25lRm9yTG9naW4iOiIxMzczODk2OTA4MyJ9fQ==; TEAMBITION_SESSIONID.sig=ZPhFOLuichYSpJod__Apg__ZRBs; TB_GTA=%7B%22pf%22%3A%7B%22cd%22%3A%22.teambition.com%22%2C%22dr%22%3A0%7D%2C%22uk%22%3A%225ecb492a1fa3311be280900d%22%7D; _bl_uid=vvldw22wytmgj1wqt181l5t2qU0q; TB_ACCESS_TOKEN=eyJhbGciOiJFZDI1NTE5IiwidHlwIjoiSldUIn0.eyJhcHAiOiI1ZDRjZWMzMGE1NWMwOTAwMDE3MWNiZDQiLCJhdWQiOiIiLCJleHAiOjE2NTMwMzI0ODYsImlhdCI6MTY1Mjc3MzI4NiwiaXNzIjoidHdzIiwianRpIjoiMmdEMEFmaUZhOHU1V3QyZ0JMNFhGejRIOTF6SjFtbmN1Y1lxWjdqQWFmZz0iLCJyZW5ld2VkIjoxNTkxNjA4OTY5MjAxLCJzY3AiOlsiYXBwX3VzZXIiXSwic3ViIjoiNWVjYjQ5MmExZmEzMzExYmUyODA5MDBkIiwidHlwIjoiYWNjZXNzX3Rva2VuIn0.mBExLK6p6CFx3WDpBRLmJ3Unof7S2NHm2xIxxwJ8xph-z9EMMxPfM7nMss8HEVL_z4Nzn1S9cZ4EeyYlWyhnCQ'
}

# 项目及对应ID字典
projectID: dict = {
    '企业码项目':'5e997e622b607a00014d6ec8',
}

# 接口的body 传参的data
body: dict = {
    "filter": {
        "isArchived": False,
        "created": parameters['filterWeek']
    },
    "selectedSection": "taskcount",
    "name": "项目概览",
    "ignoreSaved": True,
    "components": []
}

# 接口的headers配置
headers: dict = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'origin': 'https://www.teambition.com',
    'referer': 'https://www.teambition.com',
    'cookie': parameters['userCookie']
}

# 接口url
urlTemp = 'https://www.teambition.com/api/boards/tproject/tdr/report/'


# 发送钉钉消息方法
def send_message(content=''):
    secret = 'SEC04292b1495fd5f00f5a86b93a5fb55a8f5f89980183304c852445ddeda81e62e'
    accessToken = '5908f27c8748a3e39843defd8f2e3c28120f1c423eee8f5cf716169e0e11dfa6'
    timestamp = int(round(time.time()) * 1000)

    # 加密，获取sign和timestamp
    data = (str(timestamp) + '\n' + secret).encode('utf-8')
    secret = secret.encode('utf-8')
    signature = base64.b64encode(hmac.new(secret, data, digestmod=hashlib.sha256).digest())
    reg = re.compile(r"'(.*)'")
    signature = str(re.findall(reg, str(signature))[0])

    # 发送消息
    message = {'msgtype': 'text', 'text': {'content': ''}}
    message['text']['content'] = content + '\n当前时间：' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    dingUrl = 'https://oapi.dingtalk.com/robot/send?access_token=%s&sign=%s&timestamp=%s' % \
              (accessToken, signature, timestamp)
    dingHeaders = {"Content-Type": "application/json ;charset=utf-8 "}
    try:
        dingResponse = requests.post(dingUrl, headers=dingHeaders, json=message, timeout=(3, 60))

        response_msg = str(dingResponse.status_code) + ' ' + str(json.loads(dingResponse.content))
        print('钉钉消息发送结果：' + response_msg)
    except Exception as e:
        print('error: ', e)
        response_msg = e

    return response_msg


if __name__ == '__main__':

    # 每周缺陷数据
    result: dict = {}
    # 全期数据
    resultForAll: dict = {}

    # 获取数据存入result
    for key in projectID:
        url = urlTemp + projectID[key]
        response = requests.post(url, data=json.dumps(body), headers=headers)
        print(response.text)
        result[key] = json.loads(response.text)['graphData'][0]['rows']
        print(result[key])

        response = requests.post(url, data=json.dumps({"filter": {}}), headers=headers)
        # print(response.text)
        resultForAll[key] = json.loads(response.text)['graphData'][0]['rows']
        print(resultForAll[key])

    """
    整合数据信息到msg 信息格式如下：
    项目名称
    全期总数 N 本周总数 A 已完成 B 未完成 C
    """
    msg: str = '本周缺陷统计\n'
    for key in result:
        msg += key + '\n' + \
               '全期' + resultForAll[key][0][0] + ' ' + str(resultForAll[key][0][1]) + ' ' + \
               '本周' + result[key][0][0] + ' ' + str(result[key][0][1]) + ' ' + \
               result[key][1][0] + ' ' + str(result[key][1][1]) + ' ' + \
               result[key][2][0] + ' ' + str(result[key][2][1]) + '\n'
        time.sleep(2)

    # 发送钉钉消息
    send_message(msg)
