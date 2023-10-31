import json
import logging
import os
import re
import socket
import sys
import traceback
import uuid
import warnings
from datetime import datetime
from time import sleep

import certifi
import pandas as pd
import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

logger = logging.getLogger("mops")
hdlr = logging.FileHandler("mops.log", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


def get_detail(m):
    # 發言
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": "87",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "mops.twse.com.tw",
        "Origin": "https://mops.twse.com.tw",
        "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }
    payload = {
        "SEQ_NO": m.group(1),
        "SPOKE_TIME": m.group(2),
        "SPOKE_DATE": m.group(3),
        "COMPANY_ID": m.group(4),
        "skey": m.group(5),
        "step": "1",
        "TYPEK": "all",
    }
    for i in range(99):
        try:
            res = requests.post("https://mops.twse.com.tw/mops/web/ajax_t05sr01_1", data=payload, headers=headers, verify=certifi.where())
            res.raise_for_status()
            if "Too many query requests from your ip" in res.text:
                sleep(1)
                continue
            break
        except Exception as e:
            logger.info(f"retry {i+1} {str(e)}")
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            # logger.error("UnexpectedError:" + "\n" + "".join("!! " + line for line in lines))
            sleep(1)
            pass
    return res


def get_detail2(m):
    # 公告
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Length": "87",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "mops.twse.com.tw",
        "Origin": "https://mops.twse.com.tw",
        "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    }
    payload = {
        "co_id": m.group(1),
        "SKEY": m.group(2),
        "DATE1": m.group(3),
        "firstin": "true",
        #         "colorchg":"",
        #         "TYPEK":"all",
        #         "YEAR":"112",
        #         "MONTH":"03",
        #         "SDAY":"20230327",
        #         "EDAY":"20230327",
        "step": "2b",
    }
    for i in range(99):
        try:
            res = requests.post("https://mops.twse.com.tw/mops/web/ajax_t59sb01", data=payload, headers=headers, verify=certifi.where())
            res.raise_for_status()
            if "Too many query requests from your ip" in res.text:
                sleep(1)
                continue
            break
        except Exception as e:
            logger.info(f"retry {i+1} {str(e)}")
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            # logger.error("UnexpectedError:" + "\n" + "".join("!! " + line for line in lines))
            sleep(1)
            pass
    return res


logger.info("爬回即時重大訊息資訊")
stocksymbol = []
compname = []
date = []
time = []
subtitle = []
detail_list = []
for i in range(99):
    try:
        res = requests.get("https://mops.twse.com.tw/mops/web/t05sr01_1")
        res.raise_for_status()
        break
    except Exception as e:
        logger.info(f"retry home {i+1} {str(e)}")
        sleep(1)
        pass

soup = BeautifulSoup(res.text, "lxml")
for tr in soup.find_all("tr"):
    class_name = tr.get("class")
    if class_name:
        if class_name == ["even"] or class_name == ["odd"]:
            tds = tr.find_all("td")
            comp_code = tds[0].text
            comp_name = tds[1].text
            show_date = tds[2].text
            show_time = tds[3].text
            show_title = re.sub("\W+", " ", tds[4].text)
            logger.info(f"處理{i+1} {show_title}")
            stocksymbol.append(comp_code)
            compname.append(comp_name)
            date.append(show_date)
            time.append(show_time)
            subtitle.append(show_title)
            js = tds[5].find("input")["onclick"]
            m = re.match(
                "document\.fm_t05sr01_1\.SEQ_NO\.value='(\d+)';document\.fm_t05sr01_1\.SPOKE_TIME.value='(\d+)';document\.fm_t05sr01_1.SPOKE_DATE.value='(\d+)';document\.fm_t05sr01_1\.COMPANY_ID\.value='(\w+)';document\.fm_t05sr01_1\.skey\.value='(\w+)';openWindow\(this\.form ,''\);",
                js,
            )
            if m:
                res = get_detail(m)
            else:
                m = re.match(
                    "document\.t59sb01_form\.action='ajax_t59sb01';document\.t59sb01_form\.co_id\.value='(\d+)';document\.t59sb01_form\.SKEY\.value='(\d+)';document\.t59sb01_form\.DATE1\.value='(\d+)';openWindow\(document\.t59sb01_form ,''\);",
                    js,
                )
                res = get_detail2(m)

            soup = BeautifulSoup(res.text, "lxml")
            logger.info("取詳細資料裡面的說明 目前有愈到以下情況 可能有更好的寫法~")
            logger.info("另外就是 發言人 發言人職稱 發言人電話 事實發生日 或許也可以取一下值~")
            try:
                detail = soup.find_all("table")[1].find_all("td")[9].text
            except IndexError:
                detail = soup.find_all("table")[1].find_all("td")[5].text
            if len(detail) < 20:
                detail = soup.find_all("table")[1].find_all("td")[8].text
            detail_list.append(detail)

# df = pd.Data
data_1 = pd.DataFrame({"公司代號": stocksymbol, "公司簡稱": compname, "發言日期": date, "發言時間": time, "主旨": subtitle, "詳細資訊": detail_list})
data_1.to_excel("mops.xlsx", index=False)
