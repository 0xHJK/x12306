#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: config.py
@time: 2019-02-08
"""
"""
    全局配置和共享变量
"""

import platform
from os import path


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        # else:
        #     cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class Options(metaclass=Singleton):
    """
    自定义选项
    """

    def __init__(self):
        # 从哪里出发 -f --from-station
        self.fs = ""
        # 到哪里去 -t --to-station
        self.ts = ""
        # 日期 -d --date （格式：2019-01-01）
        self.date = ""
        # 车次号 -n --train-no （格式：G1 G2 G3）
        self.train_no = ""
        # 座位 -s --seats （格式：一等座 二等座 无座）
        self.seats = "一等座 二等座 无座"
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

        # dir = path.abspath(path.join(path.dirname(__file__), ".."))
        dir = path.dirname(__file__)
        # 代理文件 --proxies-file （从文件中随机读取代理）
        self.proxies_file = path.join(dir, "data", "proxies.txt")
        # 站点信息文件 --stations-file （从12306下载）
        self.stations_file = path.join(dir, "data", "stations.txt")
        # CDN文件 --cdn-file
        self.cdn_file = path.join(dir, "data", "cdn.txt")

    def __str__(self):
        """返回配置信息"""
        s1 = "出发地：%s | 目的地：%s | 日期：%s\n" % (
            self.highlight(self.fs),
            self.highlight(self.ts),
            self.highlight(self.date),
        )
        s2 = "限制车次：%s | 限制座位：%s\n" % (
            self.highlight(self.train_no or "无"),
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
