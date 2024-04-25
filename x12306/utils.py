#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: utils.py
@time: 2019-02-08
"""

import platform


def colorize(s, color):
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "pink": "\033[35m",
        "cyan": "\033[36m",
        # 高铁
        "g": "\033[91m",
        # 普通列车
        "o": "\033[92m",
        # 动车
        "d": "\033[93m",
        # 城际
        "c": "\033[93m",
        # "": "\033[94m",
        # "": "\033[95m",
        # "": "\033[96m",
    }
    if color not in colors or platform.system() == "Windows":
        return str(s)
    return colors[color] + str(s) + "\033[0m"
