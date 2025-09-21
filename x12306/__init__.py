#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: __init__.py
@time: 2019-02-08
"""
import click

from .settings import settings
from .train import TrainTable


@click.command()
@click.version_option()
@click.option("-f", "--from-station", prompt="请输入出发地", help="出发地")
@click.option("-t", "--to-station", prompt="请输入目的地", help="目的地")
@click.option("-d", "--date", prompt="请输入日期（YYYY-MM-DD）", help="日期")
@click.option("-s", "--seats", help="限制座位，如：一等座 二等座 无座")
@click.option("-n", "--trains-no", help="限制车次，如：G1 G2 G3")
@click.option("-z", "--zmode", default=False, is_flag=True, help="高级模式，查询中间站点")
@click.option("-zz", "--zzmode", default=False, is_flag=True, help="终极模式，查询所有中间站点")
@click.option("-r", "--remaining", default=False, is_flag=True, help="只看有票")
@click.option("-v", "--verbose", default=False, is_flag=True, help="调试模式")
@click.option("--gcd", default=False, is_flag=True, help="只看高铁动车城际")
@click.option("--ktz", default=False, is_flag=True, help="只看普快特快直达等")
@click.option("--proxies-file", help="代理列表文件")
@click.option("--stations-file", help="站点信息文件")
@click.option("--cdn-file", help="CDN文件")
@click.option("--csv-file", help="保存为csv文件")
def main(
    from_station,
    to_station,
    date,
    seats,
    trains_no,
    zmode,
    zzmode,
    remaining,
    verbose,
    gcd,
    ktz,
    proxies_file,
    stations_file,
    cdn_file,
    csv_file
):
    """
    12306查票助手 https://github.com/0xHJK/x12306

    Example: python3 x12306.py -f 上海 -t 北京 -d "2024-05-01"
    """
    settings.update(
        fs=from_station,
        ts=to_station,
        date=date,
        seats=seats,
        trains_no=trains_no,
        zmode=zmode,
        zzmode=zzmode,
        remaining=remaining,
        verbose=verbose,
        gcd=gcd,
        ktz=ktz,
        proxies_file=proxies_file,
        stations_file=stations_file,
        cdn_file=cdn_file,
        csv_file=csv_file
    )

    print("\n-----------------------")
    print(settings)
    print("查询中...请稍等... :)\n")
    tt = TrainTable()
    tt.update()
    tt.echo()
