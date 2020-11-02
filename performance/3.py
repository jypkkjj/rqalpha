import pandas as pd
import numpy as np
import time
import talib


# 获取过去30个交易日的fields = data_index的数据
def get_data(stock, data_index):
    # 获取过去30个交易日的fields = data_index的数据，并保存在res中
    res = history_bars(stock, 30, '1d', data_index)
    # 将type(res) 转为 numpy.array格式
    res = np.array(res)
    # 返回res的值
    return res


# 生成保存下单权重的列表
def weight_decide(res):
    # 申明alist是一个列表
    alist = []
    for i in range(len(res)):
        # 向alist中添加一个dict，key是股票名称，value是购买的比例，根据市值由小到大rank并由大到小赋权。
        alist.append({res[i]: (2 * (len(res) - i)) / ((1 + len(res)) * len(res))})
    # 返回alist
    return alist


# 生成将要购买的股票池
def choose_stocks(context):
    # 选出context.stock_list中市值最小的10支股票
    market_cap = get_fundamentals(query(fundamentals.eod_derivative_indicator.market_cap).filter(
        fundamentals.stockcode.in_(context.stock_list)).order_by(
        fundamentals.eod_derivative_indicator.market_cap).limit(10))
    # 取出这些股票代码，并赋给context.chosen
    context.chosen = list(market_cap.columns)
    pass


# 获得中证500成分股股票列表
def get_stock_list(context, bar_dict):
    # 000905.XSH  中证500(深)
    # result = index_components('000905.XSH')
    result = index_components('000001.XSHG')
    context.stock_list = result
    pass


def init(context):
    # 申明自定义全局变量 context.chosen
    context.chosen = []
    # 申明自定义全局变量 context.price_list
    context.price_list = pd.DataFrame()  # 持仓股票的若干天收盘价
    # 申明自定义全局变量 context.stock_list
    context.stock_list = []  # 中证500 成分股股票池
    # 每月第10个交易日调用get_stock_list函数，更新中证500股票池。
    scheduler.run_monthly(get_stock_list, tradingday=10)
    pass


def before_trading(context):
    # 将中证500成分股赋给context.stock_list
    context.stock_list = index_components('中证500(深)')
    # 生成将要购买的股票池
    choose_stocks(context)
    # 时间戳转换，start_date(st)和end_date(ed)
    ts = time.strptime(str(context.now), "%Y-%m-%d %H:%M:%S")
    st = int(time.mktime(ts)) - 24 * 3600 * 5
    st = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st))
    ed = int(time.mktime(ts)) - 24 * 3600 * 1
    ed = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ed))
    # 如果目前有持仓：
    if list(context.portfolio.positions.keys()):
        # 取出持仓股票在st至ed时间之间的收盘价，结果传入context.price_list
        context.price_list = get_price(list(context.portfolio.positions.keys()), start_date=st, end_date=ed,
                                       fields='close')
    pass


def handle_bar(context, bar_dict):
    # 遍历持仓股票
    for stock in list(context.portfolio.positions.keys()):
        # 获得近30个交易日的TRANGE技术指标，并转格式为pd.Series()
        res = pd.Series(talib.TRANGE(get_data(stock, 'high'), get_data(stock, 'low'), get_data(stock, 'close')))
        try:
            # 若stock昨日收盘价-前日收盘价 < -0.95倍的昨日TRANGE
            if context.price_list[stock].iloc[-1] - context.price_list[stock].iloc[-2] < -0.95 * res.iloc[-2]:
                # 卖出所有持仓股票（目标仓位为0）
                order_target_percent(stock, 0)
        except:
            # 若stock不在context的列名中
            if stock not in context.price_list.columns:
                # 卖出所有持仓股票（目标仓位为0）
                order_target_percent(stock, 0)
    # 调用weight_decide函数，生成保存下单权重的列表，并将结果保存在alist中。
    alist = weight_decide(context.chosen)
    for stock in alist:
        # 按权重下单（目标仓位保存在weight_decide的value中）
        order_target_percent(list(stock.keys())[0], list(stock.values())[0])
    pass


def after_trading(context):
    pass


CONFIG = {
    "base": {
        "start_date": "20190901",
        "end_date": "20200901",
        "frequency": "1d",
        # "benchmark": "000300.XSHG",
        "accounts": {
            "STOCK": 10e8
        }
    },
    "extra": {
        "log_level": "verbose"
    },
    "mod": {
        "sys_analyser": {
            "enabled": True,
            # "report_save_path": ".",
            "plot": True,
            "enabled": True,
            "benchmark": "000300.XSHG"
            # "matching_type": "last"
        },
    }
}

# 上证综指，深证成指，上证50，中证500，中小板指，创业板指
def get_index_components(trade_date):
    import tushare as ts
    # 设置token
    ts.set_token('456b1cb6d086872e59ffd4432c0ef6bc31fa1e6450a3d8b89a1d667d')
    # 初始化pro接口
    pro = ts.pro_api()
    # index_weight
    df = pro.index_weight(index_code='000905.SH', start_date=trade_date)
    return list(df['con_code'])


if __name__ == "__main__":
    from rqalpha import run_func
    # run_func(init=init, handle_bar=handle_bar, config=CONFIG)
    print(get_index_components("20180901"))
