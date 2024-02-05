#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: request.py
@time: 2019-02-08
"""

import random
import requests

from .glovar import Glovar, FAKE_HEADERS


class Request:
    """
    封装requests
    """

    def get_available_proxy(self) -> str:
        """
            获得一个可用的代理
        :return: 返回一个可用代理或空字符串
        """
        glovar = Glovar()
        if not glovar.total_proxies:
            # 如果没有可用代理则返回空字符串
            return ""

        proxy = random.choices(glovar.total_proxies)
        s = requests.Session()
        s.headers.update(FAKE_HEADERS)
        s.proxies.update({"http": proxy, "https": proxy})

        try:
            r = s.get("https://kyfw.12306.cn/otn/leftTicket/init", timeout=5)
            if r.status_code != requests.codes.ok or len(r.content) < 100:
                # 状态码不成功或内容长度太短也判定为失败
                raise RuntimeError
            else:
                return proxy
        except Exception:
            # 如果请求失败则从代理列表中删除
            glovar.total_proxies.remove(proxy)
            # 递归请求
            return self.get_available_proxy()

    def get_session(self):
        """ 获得一个session对象 """
        s = requests.Session()
        s.headers.update(FAKE_HEADERS)
        proxy = self.get_available_proxy()
        if proxy:
            s.proxies.update({"http": proxy, "https": proxy})
        return s
