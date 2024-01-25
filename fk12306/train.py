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
import prettytable as pt

from .glovar import Glovar, QUERY_URL
from .request import Request
from .utils import code_to_station, station_to_code, colorize


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
        # 途经的车站（站编码，站名，到达时间）元组
        self.stations = []

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
        """ 车次、出发站和目的地相同判断为相等 """
        return (
            self.full_no == other.full_no
            and self._fs == other._fs
            and self._ts == other._ts
        )

    def __lt__(self, other):
        """ 根据车次号排序 """
        return self.start_time < other.start_time

    def __gt__(self, other):
        """ 根据车次号排序 """
        return self.start_time > other.start_time

    @property
    def fs_code(self):
        return self._fs_code

    @fs_code.setter
    def fs_code(self, fs_code):
        self._fs_code = fs_code
        self._fs = code_to_station(fs_code)

    @property
    def ts_code(self):
        return self._ts_code

    @ts_code.setter
    def ts_code(self, ts_code):
        self._ts_code = ts_code
        self._ts = code_to_station(ts_code)

    @property
    def has_remaining(self) -> bool:
        for r in self.remaining:
            if r != "无" and r != "--":
                return True
        return False

    @property
    def row(self) -> list:
        """ 关键信息列表 """
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

    def update_stations(self):
        """
            更新train对象中沿途车站的信息
        :param train: Train对象
        :param kwargs:
        :return: 无返回
        """
        glovar = Glovar()
        req = Request()
        s = req.get_session()

        # 准备请求参数
        params = {
            "train_no": self.full_no,
            "from_station_telecode": self.fs_code,
            "to_station_telecode": self.ts_code,
            "depart_date": glovar.date,
        }
        # 发送请求
        r = s.get(
            "https://kyfw.12306.cn/otn/czxx/queryByTrainNo", params=params, timeout=10
        )
        j = r.json()
        for item in j["data"]["data"]:
            if not item["isEnabled"]:
                continue
            station_code = station_to_code(item["station_name"])
            self.stations.append(
                (station_code, item["station_name"], item["arrive_time"])
            )


class TrainTable:
    """
    搜索结果列表
    """

    def __init__(self):
        self.trains_list = []

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

    def cleanup(self):
        """ 处理trains_list，排序和删除无效数据 """
        glovar = Glovar()
        t_list = []
        if glovar.remaining:
            for train in self.trains_list:
                # print(train.no, train.remaining, train.has_remaining)
                if train.has_remaining:
                    t_list.append(train)
        else:
            t_list = self.trains_list
        self.trains_list = sorted(t_list)

    def update_trains(self, **kwargs):
        """
            对外调用的方法，查询12306列车信息，把结果更新到trains_list中
        :param kwargs:
        """
        glovar = Glovar()

        fs = kwargs.get("fs", "")
        ts = kwargs.get("ts", "")
        if fs and ts:
            # 优先处理fs和ts
            fs_code = station_to_code(fs)
            ts_code = station_to_code(ts)
        else:
            # 如果没有则再处理fs_code和ts_code
            fs_code = kwargs.get("fs_code", glovar.fs_code)
            ts_code = kwargs.get("ts_code", glovar.ts_code)

        date = kwargs.get("date", glovar.date)
        no_list = kwargs.get("no_list", glovar.no_list)

        if kwargs.get("zmode", glovar.zmode):
            self.trains_list = self._query_trains_zmode(fs_code, ts_code, date, no_list)
        else:
            self.trains_list = self._query_trains_basic(fs_code, ts_code, date, no_list)

    def _query_trains_basic(self, fs_code, ts_code, date, no_list) -> list:
        """
            普通查询方法，根据出发地和目的地编码、日期和限制车次，返回trains列表
            仅被内部调用，调用前处理好参数
        :param fs_code: 出发地编码
        :param ts_code: 目的地编码
        :param date: 日期
        :param no_list: 选择车次列表
        :return: 返回搜索结果列表，每一项是一个Train对象
        """
        glovar = Glovar()
        req = Request()
        s = req.get_session()
        # 准备请求参数
        params = {
            "leftTicketDTO.train_date": date,
            "leftTicketDTO.from_station": fs_code,
            "leftTicketDTO.to_station": ts_code,
            "purpose_codes": "ADULT",
        }
        try:
            # 发送请求
            print(params)
            r = s.get(
                QUERY_URL, params=params, timeout=10
            )
            j = r.json()
            raws = j["data"]["result"]
            # 处理返回结果
            train_list = []
            for raw in raws:
                fields = raw.split("|")
                # 如果限制了车次，且搜索车次不在目标车次中则丢弃
                if no_list and fields[3] not in no_list:
                    continue
                # 如果限制了种类
                if glovar.gcd:
                    # 只看高铁动车城际
                    if fields[3][0] not in "GCD":
                        continue
                elif glovar.ktz:
                    # 只看普通列车
                    if fields[3][0] in "GCD":
                        continue

                train = Train()
                train.full_no = fields[2]  # 编号全称
                train.no = fields[3]  # 编号简称
                train.fs_code = fields[6]
                train.ts_code = fields[7]
                train.start_time = fields[8]
                train.end_time = fields[9]
                train.duration = fields[10]
                for i in glovar.seats_idx_list:
                    train.remaining.append(fields[i] or "--")
                train_list.append(train)
        except Exception as e:
            print(e)
            print(r.text)
            print(s.headers)
            train_list = []
        return train_list

    def _query_trains_zmode(self, fs_code, ts_code, date, no_list) -> list:
        """
            高级查询模式，会查询从出发站到沿途所有站的车次情况
            仅被内部调用，调用前处理好参数
        :param fs_code: 出发地编码
        :param ts_code: 目的地编码
        :param date: 日期
        :param no_list: 限制车次
        :return: Train对象列表
        """
        # stations_set = set()
        stations_dict = {}
        trains_list = self._query_trains_basic(fs_code, ts_code, date, no_list)
        try:
            for train in trains_list:
                train.update_stations()
                for station in train.stations[1:-1]:  # 除了出发站和目标站本身
                    # stations_set.add(station[0])
                    if station[0] in stations_dict:
                        stations_dict[station[0]].append(train.no)
                    else:
                        stations_dict[station[0]] = [train.no]
            for station, trains in stations_dict.items():
                time.sleep(1)
                trains_list += self._query_trains_basic(fs_code, station, date, trains)
        except Exception as e:
            print(e)
        finally:
            return trains_list
