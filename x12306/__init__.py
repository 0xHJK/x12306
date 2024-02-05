#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: __init__.py
@time: 2019-02-08
"""

import click

from .config import Options
from .glovar import Glovar
from .train import TrainTable


@click.command()
@click.version_option()
@click.option("-f", "--from-station", prompt="请输入出发地", help="出发地")
@click.option("-t", "--to-station", prompt="请输入目的地", help="目的地")
@click.option("-d", "--date", prompt="请输入日期（YYYY-MM-DD）", help="日期")
@click.option("-s", "--seats", help="限制座位")
@click.option("-n", "--train-no", help="限制车次")
@click.option("-z", "--zmode", default=False, is_flag=True, help="高级模式，查询中间站点")
@click.option("-zz", "--zzmode", default=False, is_flag=True, help="终极模式，查询所有中间站点")
@click.option("-r", "--remaining", default=False, is_flag=True, help="只看有票")
@click.option("--gcd", default=False, is_flag=True, help="只看高铁动车城际")
@click.option("--ktz", default=False, is_flag=True, help="只看普快特快直达等")
@click.option("--proxies-file", help="代理列表文件")
@click.option("--stations-file", help="站点信息文件")
@click.option("--cdn-file", help="CDN文件")
def main(
    from_station,
    to_station,
    date,
    seats,
    train_no,
    zmode,
    zzmode,
    remaining,
    gcd,
    ktz,
    proxies_file,
    stations_file,
    cdn_file,
):
    """
    12306查票助手 https://github.com/0xHJK/x12306

    Example：python x12306.py -f 上海 -t 北京 -d "2019-03-01" -n "G16 G18 G22" -r

    如果查询失败的话，请修改glovar.py中的QUERY_URL和JSESSIONID
    """
    opts = Options()
    opts.fs = from_station
    opts.ts = to_station
    if date:
        opts.date = date
    if seats:
        opts.seats = seats
    if train_no:
        opts.train_no = train_no
    opts.zmode = zmode
    opts.zzmode = zzmode
    opts.gcd = gcd
    opts.ktz = ktz
    opts.remaining = remaining
    if proxies_file:
        opts.proxies_file = proxies_file
    if stations_file:
        opts.stations_file = stations_file
    if cdn_file:
        opts.cdn_file = cdn_file

    print("\n-----------------------")
    print(opts)
    tt = TrainTable()
    tt.update_trains()
    tt.echo()
