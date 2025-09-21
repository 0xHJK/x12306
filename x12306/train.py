#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: HJK
@file: train.py
@time: 2019-02-08
"""
"""
    搜索结果中的班次信息
"""

import time
import re
import requests
import prettytable as pt
import csv

from .settings import settings
from .utils import colorize


class Train:
    """
    搜索结果中的班次信息，包括车次号、余票、时间等信息
    """

    def __init__(self):
        self.full_no = ""  # 编号全称
        self.no = ""  # 编号简称
        self._fs_code = ""
        self._ts_code = ""
        self._fs = ""
        self._ts = ""
        self.start_time = ""
        self.end_time = ""
        self.duration = ""
        self.remaining = []

    def __str__(self):
        colored_remaining = [
            colorize(s, "green") if s != "无" and s != "--" else s
            for s in self.remaining
        ]
        remaining_seats = "/".join(colored_remaining)
        if re.match("[GCD]", self.no):
            colored_no = colorize(self.no, self.no[0].lower())
        else:
            colored_no = colorize(self.no, "o")
        s = "{:^5} | {:^5} | {:\u3000<4} | {:\u3000<4} | {:^5} | {} | {:^5}".format(
            colored_no,
            self.start_time,
            self._fs,
            self._ts,
            self.end_time,
            remaining_seats,
            self.duration,
        )
        return s

    def __eq__(self, other):
        """车次、出发站和目的地相同判断为相等"""
        return (
            self.full_no == other.full_no
            and self._fs == other._fs
            and self._ts == other._ts
        )
    
    def __hash__(self) -> int:
        return hash((self.full_no, self._fs, self._ts))

    def __lt__(self, other):
        """根据车次号排序"""
        return self.start_time < other.start_time

    def __gt__(self, other):
        """根据车次号排序"""
        return self.start_time > other.start_time

    @property
    def fs_code(self):
        return self._fs_code

    @fs_code.setter
    def fs_code(self, fs_code):
        self._fs_code = fs_code
        self._fs = settings.reverse_stations_dict.get(fs_code, "")

    @property
    def ts_code(self):
        return self._ts_code

    @ts_code.setter
    def ts_code(self, ts_code):
        self._ts_code = ts_code
        self._ts = settings.reverse_stations_dict.get(ts_code, "")

    @property
    def has_remaining(self) -> bool:
        for r in self.remaining:
            if r != "无" and r != "--":
                return True
        return False

    @property
    def row(self) -> list:
        """关键信息列表"""
        colored_remaining = [
            colorize(s, "green") if s != "无" and s != "--" else s
            for s in self.remaining
        ]
        remaining_seats = "/".join(colored_remaining)
        if re.match("[GCD]", self.no):
            colored_no = colorize(self.no, self.no[0].lower())
        else:
            colored_no = colorize(self.no, "o")
        return [
            colored_no,
            self.start_time,
            self._fs,
            self._ts,
            self.end_time,
            remaining_seats,
            self.duration,
        ]


class TrainTable:
    """
    搜索结果列表
    """

    def __init__(self):
        self.trains_list = []
        self._session = requests.Session()
        self._session.headers.update(settings.headers)

    @property
    def session(self):
        # TODO: 设置代理、随机headers等
        return self._session

    def echo(self):
        """
        对外调用的方法，用来打印查询结果
        """
        tb = pt.PrettyTable()
        tb.field_names = ["车次", "发车", "出发站", "到达站", "到达", "余票", "历时"]
        self.cleanup()
        for train in self.trains_list:
            tb.add_row(train.row)
        print(tb)
        if settings.csv_file:  
            with open(settings.csv_file, mode='w+', encoding='utf-8', newline='') as file:
                csv_writer = csv.writer(file)
                for train in self.trains_list:
                    csv_writer.writerow(train.row)
            print("已写入",settings.csv_file)


    def cleanup(self):
        """处理trains_list，排序和删除无效数据"""
        t_list = []
        if settings.remaining:
            for train in self.trains_list:
                # print(train.no, train.remaining, train.has_remaining)
                if train.has_remaining:
                    t_list.append(train)
        else:
            t_list = self.trains_list
        self.trains_list = sorted(t_list)

    def update(self):
        """
        对外调用的方法，查询12306列车信息，把结果更新到trains_list中
        """
        if settings.zmode:
            self.trains_list = self._query_trains_zmode(
                settings.fs_code,
                settings.ts_code,
                settings.date,
                settings.trains_no_list,
            )
        elif settings.zzmode:
            self.trains_list = self._query_trains_zzmode(
                settings.fs_code,
                settings.ts_code,
                settings.date,
                settings.trains_no_list,
            )
        else:
            self.trains_list = self._query_trains(
                settings.fs_code,
                settings.ts_code,
                settings.date,
                settings.trains_no_list,
            )

    def _query(self, url, params, retries=1) -> dict:
        """
            查询方法，根据url和参数，返回json对象
        :param url: 查询url
        :param params: 查询参数
        :param retries: 重试次数
        :return: 返回json对象
        """
        s = self.session
        # print("查询中...", " ".join([v for v in params.values()]))

        try:
            r = s.get(url, params=params, timeout=settings.timeout)
            j = r.json()
            if settings.verbose:
                print(url, params)
                print('\n[REQUEST HEADERS]', s.headers)
                print('\n[RESPONSE HEADERS]', r.headers)
                print('\n[RESPONSE TEXT]', r.text)
        except Exception as e:
            print(colorize("第 %i 查询失败" % retries, "red"), e)
            print(url, params)
            print(s.headers)
            if retries < settings.max_retries:
                time.sleep(retries * settings.timeout)
                return self._query(url, params, retries + 1)
            else:
                j = {}
        return j

    def _query_stations(self, train) -> list:
        """
            查询沿途车站信息
        :param train: Train对象
        """
        stations_list = []
        # 准备请求参数
        params = {
            "train_no": train.full_no,
            "from_station_telecode": train.fs_code,
            "to_station_telecode": train.ts_code,
            "depart_date": settings.date,
        }
        j = self._query(settings.trainno_url, params)
        if j and j.get("data") and j["data"].get("data"):
            for item in j["data"]["data"]:
                if item["isEnabled"]:
                    stations_list.append(item["station_name"])
            stations_list = stations_list[1:-1]  # 除了出发站和目标站本身
        return stations_list

    def _query_trains(self, fs_code, ts_code, date, trains_no_list) -> list:
        """
            普通查询方法，根据出发地和目的地编码、日期和限制车次，返回trains列表
            仅被内部调用，调用前处理好参数
        :param fs_code: 出发地编码
        :param ts_code: 目的地编码
        :param date: 日期
        :param trains_no_list: 选择车次列表
        :return: 返回搜索结果列表，每一项是一个Train对象
        """
        # 准备请求参数
        params = {
            "leftTicketDTO.train_date": date,
            "leftTicketDTO.from_station": fs_code,
            "leftTicketDTO.to_station": ts_code,
            "purpose_codes": "ADULT",
        }
        trains_list = []
        j = self._query(settings.query_url, params)
        if j and j.get("data") and j["data"].get("result"):
            raws = j["data"]["result"]
            # 处理返回结果
            for raw in raws:
                fields = raw.split("|")
                # 如果限制了车次，且搜索车次不在目标车次中则丢弃
                if trains_no_list and fields[3] not in trains_no_list:
                    continue
                if settings.gcd and fields[3][0] not in "GCD":
                    # 只看高铁动车城际
                    continue
                if settings.ktz and fields[3][0] in "GCD":
                    # 只看普通列车
                    continue

                train = Train()
                train.full_no = fields[2]  # 编号全称
                train.no = fields[3]  # 编号简称
                train.fs_code = fields[6]
                train.ts_code = fields[7]
                train.start_time = fields[8]
                train.end_time = fields[9]
                train.duration = fields[10]
                for i in settings.seats_code_list:
                    train.remaining.append(fields[i] or "--")
                trains_list.append(train)
        return trains_list

    def _query_trains_zmode(self, fs_code, ts_code, date, trains_no_list) -> list:
        """
            高级查询模式，会查询从出发站到沿途所有站的车次情况
            仅被内部调用，调用前处理好参数
        :param fs_code: 出发地编码
        :param ts_code: 目的地编码
        :param date: 日期
        :param trains_no_list: 限制车次
        :return: Train对象列表
        """
        trains_list = self._query_trains(fs_code, ts_code, date, trains_no_list)
        trains_no_list = [train.no for train in trains_list]
        stations_list = []

        for train in trains_list:
            stations_list += self._query_stations(train)
        stations_list = list(set(stations_list))

        for station in stations_list:
            ts_code = settings.stations_dict.get(station, "")
            if ts_code:
                trains_list += self._query_trains(
                    fs_code, ts_code, date, trains_no_list
                )

        return list(set(trains_list))
    def _query_trains_zzmode(self, fs_code, ts_code, date, trains_no_list) -> list:
        """
            高级查询模式，会查询从出发站到沿途所有站的车次情况
            仅被内部调用，调用前处理好参数
        :param fs_code: 出发地编码
        :param ts_code: 目的地编码
        :param date: 日期
        :param trains_no_list: 限制车次
        :return: Train对象列表
        """
        trains_list = self._query_trains(fs_code, ts_code, date, trains_no_list)
        trains_no_list = [train.no for train in trains_list]
        stations_list = []

        for train in trains_list:
            stations_list += self._query_stations(train)
        stations_list = list(set(stations_list))
        for station in stations_list:
            nfs_code = settings.stations_dict.get(station, "")
            if ts_code:
                trains_list += self._query_trains_zmode(
                    nfs_code, ts_code, date, trains_no_list
                )

        return list(set(trains_list))
