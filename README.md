# fk12306

12306查票助手，一键查询沿途所有站点，先上车后补票，暂不支持抢票

`fk`的意思是`Find and checK`，也就是`F*** *** ****K`，缩写为`fk`

仅支持Python3，推荐Python3.5+


## 安装

**安装前修改glovar.py中FAKE_HEADERS的Cookie值，从浏览器中复制即可**

手动安装：
```bash
git clone https://github.com/0xHJK/fk12306
cd fk12306 && make install
```

不安装直接运行：
```bash
git clone https://github.com/0xHJK/fk12306
cd fk12306
python3 fk12306.py
```

## 使用方法

```
$ fk12306 --help
Usage: fk12306 [OPTIONS]

  12306查票助手 Example：fk12306 -f 上海 -t 北京 -d "2019-03-01" -n "G16 G18 G22" -r

Options:
  --version                Show the version and exit.
  -f, --from-station TEXT  出发地
  -t, --to-station TEXT    目的地
  -d, --date TEXT          日期
  -s, --seats TEXT         限制座位
  -n, --train-no TEXT      限制车次
  -z, --zmode              高级模式
  -zz, --zzmode            终极模式
  -r, --remaining          只看有票
  --gcd                    只看高铁动车城际
  --ktz                    只看普快特快直达等
  --proxies-file TEXT      代理列表文件
  --stations-file TEXT     站点信息文件
  --cdn-file TEXT          CDN文件
  --help                   Show this message and exit.
```

## 使用示例

![](https://github.com/0xHJK/fk12306/raw/master/docs/preview.png)

## LICENSE
[MIT License](https://github.com/0xHJK/fk12306/blob/master/LICENSE)
