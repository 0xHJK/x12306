#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: settings.py
@time: 2024-04-24
"""

"""
全局配置和共享变量，统一config和glovar
"""

import re
import sys
import platform
import hashlib
import secrets
import requests
from os import path
# from fake_useragent import UserAgent

# 默认配置
SEAT_TYPES = {
    "特等座": 25,
    "商务座": 32,
    "一等座": 31,
    "二等座": 30,
    "高级软卧": 21,
    "软卧": 23,
    "动卧": 33,
    "硬卧": 28,
    "软座": 24,
    "硬座": 29,
    "无座": 26,
    "其他": 22,
}
DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "kyfw.12306.cn",
    "Referer": "https://kyfw.12306.cn/otn/leftTicket/init",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": "JSESSIONID=" + hashlib.md5(secrets.token_bytes(16)).hexdigest().upper(),
}

DEFAULT_SEATS = "一等座 二等座 无座"
DEFAULT_PROXIES_FILE = path.join(path.dirname(__file__), "data", "proxies.txt")
DEFAULT_STATIONS_FILE = path.join(path.dirname(__file__), "data", "stations.txt")
DEFAULT_CDN_FILE = path.join(path.dirname(__file__), "data", "cdn.txt")

DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 5
DEFAULT_BASE_URL = "https://kyfw.12306.cn/otn/leftTicket"
DEFAULT_TRAINNO_URL = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo"


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Settings(metaclass=Singleton):
    """
    全局配置和共享变量
    """

    def __init__(self):
        # 从哪里出发 -f --from-station
        self.fs = ""
        # 到哪里去 -t --to-station
        self.ts = ""
        # 日期 -d --date （格式：2019-01-01）
        self.date = ""
        # 车次代码 -n --trains-no （格式：G1 G2 G3）
        self.trains_no = ""
        # 座位 -s --seats （格式：一等座 二等座 无座）
        self.seats = DEFAULT_SEATS
        # 高级模式 -z --zmode （查询始发站往后到沿途的站点是否有票）
        self.zmode = False
        # 终极模式 -zz --zzmode （查询沿途所有站点之间是否有票）
        self.zzmode = False
        # 只看高铁动车城际 -g --gcd
        self.gcd = False
        # 只看普通列车（非gcd）-k --ktz
        self.ktz = False
        # 只看有余票 -r --remaining
        self.remaining = False
        # debug模式 -v --verbose
        self.verbose = False

        # 代理文件 --proxies-file （从文件中随机读取代理）
        self.proxies_file = DEFAULT_PROXIES_FILE
        # 站点信息文件 --stations-file （从12306下载）
        self.stations_file = DEFAULT_STATIONS_FILE
        # CDN文件 --cdn-file
        self.cdn_file = DEFAULT_CDN_FILE
        # CDN文件 --csv-file
        self.csv_file = None

        self.headers = DEFAULT_HEADERS
        self.init_url = DEFAULT_BASE_URL + "/init"
        self.query_url = DEFAULT_BASE_URL + "/query"
        self.trainno_url = DEFAULT_TRAINNO_URL
        self.timeout = DEFAULT_TIMEOUT
        self.max_retries = DEFAULT_MAX_RETRIES

        self._stations_dict = {}

    @property
    def stations_dict(self):
        # {站名：编码} 如 {北京：VAP}
        if self._stations_dict:
            return self._stations_dict
        else:
            self.update_stations()
            return self._stations_dict

    @property
    def reverse_stations_dict(self):
        # {编码：站名} 如 {VAP：北京}
        return {v: k for k, v in self.stations_dict.items()}

    @property
    def proxies_list(self):
        if self._proxies_list:
            return self._proxies_list
        else:
            self.update_proxies()
            return self._proxies_list

    @property
    def fs_code(self):
        return self.stations_dict.get(self.fs, "")

    @property
    def ts_code(self):
        return self.stations_dict.get(self.ts, "")

    @property
    def trains_no_list(self):
        if self.trains_no:
            separators = "[,; ]"  # comma, semicolon, and space
            return re.split(separators, self.trains_no.upper())
        else:
            return []

    @property
    def seats_list(self):
        # 获得座位列表
        return [s for s in self.seats.split() if s in SEAT_TYPES]

    @property
    def seats_code_list(self):
        # 获得座位编号列表
        return [SEAT_TYPES[s] for s in self.seats_list]

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None and hasattr(self, k):
                setattr(self, k, v)

        self.update_stations()
        self.update_proxies()
        self.update_query_url()

    def update_stations(self):
        # 如果stations文件不存在则终止程序
        if not path.isfile(self.stations_file):
            print(self.stations_file)
            print("Stations file is not exsits.")
            sys.exit(-1)

        # 更新站点信息
        stations = open(self.stations_file, "r", encoding="utf-8").read()
        for station in stations.split("@"):
            if not station:
                continue
            t = station.split("|")
            # {站名：编码} 如 {北京：VAP}
            self._stations_dict[t[1]] = t[2]

    def update_proxies(self):
        # 更新代理信息
        if path.isfile(self.proxies_file):
            # 如果代理列表文件存在
            self._proxies_list = open(
                self.proxies_file, "r", encoding="utf-8"
            ).readlines()

    def update_query_url(self):
        try:
            r = requests.get(self.init_url, headers=self.headers, timeout=self.timeout)
            if r.status_code == 200:
                m = re.search(r"var CLeftTicketUrl = \'(.*?)\'", r.text)
                self.query_url = DEFAULT_BASE_URL + "/" + m.group(1).split("/")[1]
            else:
                print("Failed to update query url.")
                sys.exit(-1)
        except Exception as e:
            print(e)
            print("Failed to update query url.")
            sys.exit(-1)

    def __str__(self):
        """返回配置信息"""
        s1 = "出发地：%s | 目的地：%s | 日期：%s\n" % (
            self.highlight(self.fs),
            self.highlight(self.ts),
            self.highlight(self.date),
        )
        s2 = "限制车次：%s | 限制座位：%s\n" % (
            self.highlight(self.trains_no or "无"),
            self.highlight(self.seats),
        )
        s3 = "只看高铁动车：%s | 只看普通列车：%s\n" % (
            self.highlight(self.gcd),
            self.highlight(self.ktz),
        )
        s4 = "高级模式：%s | 终极模式：%s | 只看有票：%s\n" % (
            self.highlight(self.zmode),
            self.highlight(self.zzmode),
            self.highlight(self.remaining),
        )
        return s1 + s2 + s3 + s4

    def highlight(self, s):
        if platform.system() == "Windows":
            return str(s)
        return "\033[33m" + str(s) + "\033[0m"


settings = Settings()
