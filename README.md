# x12306

12306查票助手，主要功能是可以一键查询沿途所有站点。

当全程票售罄的时候，方便查询中间站点余票，先上车后补票。

工具仅用于查询余票，不支持购票，建议在12306官方平台购票。

仅支持Python3，推荐Python3.7+

**⚠️短时间内多次查询可能会被屏蔽，可以过一会再查询**

**如果对你有帮助，可以请我喝一杯咖啡 <https://hjk.im/donate>**

## 安装运行

pip安装
```bash
pip install x12306
```

手动安装：
```bash
git clone https://github.com/0xHJK/x12306
cd x12306 && make install
```

不安装直接运行：
```bash
git clone https://github.com/0xHJK/x12306
cd x12306
python3 x12306.py -f <出发地> -t <目的地> -d <YYYY-MM-DD>
```

## 使用说明

示例

```bash
# 查询2024年5月1日，上海到北京的车票
python3 x12306.py -f 上海 -t 北京 -d "2024-05-01"

# 查询2024年5月1日，上海到北京的车票，只看有余票
python3 x12306.py -f 上海 -t 北京 -d "2024-05-01" -r

# 查询2024年5月1日，上海到北京的车票，只看动车高铁
python3 x12306.py -f 上海 -t 北京 -d "2024-05-01" --gcd

# 查询2024年5月1日，上海到北京的车票，只看普速火车
python3 x12306.py -f 上海 -t 北京 -d "2024-05-01" --ktz

# 查询2024年5月1日，上海到北京的车票，只看特定车次
python3 x12306.py -f 上海 -t 北京 -d "2024-05-01" -n "G26 G28"

# 查询2024年5月1日，上海到北京的车票，只看商务座和一等座
python3 x12306.py -f 上海 -t 北京 -d "2024-05-01" -s "商务座 一等座" -r

# 查询2024年5月1日，上海到北京的车票，并查询上海出发沿途所有车站是否有票
python3 x12306.py -f 上海 -t 北京 -d "2024-05-01" -z -r
```

帮助

```bash
$ python x12306.py --help
Usage: x12306.py [OPTIONS]

  12306查票助手 https://github.com/0xHJK/x12306

  Usage: python3 x12306.py -f <出发地> -t <目的地> -d <YYYY-MM-DD>

  Example: python3 x12306.py -f 上海 -t 北京 -d "2024-05-01"

Options:
  --version                Show the version and exit.
  -f, --from-station TEXT  出发地
  -t, --to-station TEXT    目的地
  -d, --date TEXT          日期
  -s, --seats TEXT         限制座位，如：一等座 二等座 无座
  -n, --trains-no TEXT     限制车次，如：G1 G2 G3
  -z, --zmode              高级模式，查询中间站点
  -zz, --zzmode            终极模式，查询所有中间站点
  -r, --remaining          只看有票
  -v, --verbose            调试模式
  --gcd                    只看高铁动车城际
  --ktz                    只看普快特快直达等
  --proxies-file TEXT      代理列表文件
  --stations-file TEXT     站点信息文件
  --cdn-file TEXT          CDN文件
  --help                   Show this message and exit.
```


![](https://github.com/0xHJK/x12306/raw/master/docs/preview.png)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=0xHJK/x12306&type=Date)](https://star-history.com/#0xHJK/x12306&Date)

## LICENSE

[MIT License](https://github.com/0xHJK/x12306/blob/master/LICENSE)