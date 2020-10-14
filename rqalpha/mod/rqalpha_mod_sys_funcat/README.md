[github](https://github.com/ricequant/rqalpha-mod-funcat)



# RQAlpha Funcat Mod

该模块为 RQAlpha 带来了以通达信公式的方式编写策略逻辑的功能。

启用该 Mod ，会自动将 [funcat](https://github.com/cedricporter/funcat) 注入 API 到 RQAlpha 中。



## 开启或关闭 Mod

```
# 启用 funcat API Mod
$ rqalpha mod enable funcat

# 关闭 funcat API Mod
$ rqalpha mod disable funcat
```



## 常用API定义



### 行情变量

- 开盘价：`OPEN` `O`
- 收盘价：`CLOSE` `C`
- 最高价：`HIGH` `H`
- 最低价：`LOW` `L`
- 成交量：`VOLUME` `V`



### 工具函数

- n天前的数据：REF

```
REF(C, 10) # 10天前的收盘价
```

- 金叉判断：CROSS

```
CROSS(MA(C, 5), MA(C, 10)) # 5日均线上穿10日均线
```

- 两个序列取最小值：MIN

```
MIN(O, C) # K线实体的最低价
```

- 两个序列取最大值：MAX

```
MAX(O, C) # K线实体的最高价
```

- n天都满足条件：EVERY

```
EVERY(C > MA(C, 5), 10) # 最近10天收盘价都大于5日均线
```

- n天内满足条件的天数：COUNT

```
COUNT(C > O, 10) # 最近10天收阳线的天数
```

- n天内最大值：HHV

```
HHV(MAX(O, C), 60) # 最近60天K线实体的最高价
```

- n天内最小值：LLV

```
LLV(MIN(O, C), 60) # 最近60天K线实体的最低价
```

- 求和n日数据 SUM

```
SUM(C, 10) # 求和10天的收盘价
```

- 求绝对值 ABS

```
ABS(C - O)
```



## API样例策略

```
from rqalpha.api import *


def init(context):
    context.s1 = "600275.XSHG"


def handle_bar(context, bar_dict):
    S(context.s1)
    # 自己实现 DMA指标（Different of Moving Average）
    M1 = 5
    M2 = 89
    M3 = 36

    DDD = MA(CLOSE, M1) - MA(CLOSE, M2)
    AMA = MA(DDD, M3)

    cur_position = context.portfolio.positions[context.s1].quantity

    if DDD < AMA and cur_position > 0:
        order_target_percent(context.s1, 0)

    if (HHV(MAX(O, C), 50) / LLV(MIN(O, C), 50) < 2
        and CROSS(DDD, AMA) and cur_position == 0):
        order_target_percent(context.s1, 1)
```



## 更多 API 介绍

请见 [funcat](https://github.com/cedricporter/funcat) 。