#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: fk12306.py
@time: 2019-02-08

启动入口

"""

import os, sys

_srcdir = "%s/" % os.path.dirname(os.path.realpath(__file__))
_filepath = os.path.dirname(sys.argv[0])
sys.path.insert(1, os.path.join(_filepath, _srcdir))

if sys.version_info[0] == 3:
    import fk12306

    if __name__ == "__main__":
        fk12306.main()
else:  # Python 2
    print("Python3 Only.")
