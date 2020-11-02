"""
https://blog.ricequant.com/2020/08/07/%e6%88%91%e6%9c%89%e4%b8%80%e4%b8%aa%e7%ad%96%e7%95%a5%e6%83%b3%e6%b3%95%ef%bc%8c%e5%a6%82%e4%bd%95%e4%b8%80%e6%ad%a5%e6%ad%a5%e8%bd%ac%e5%8c%96%e6%88%90%e7%ad%96%e7%95%a5%e4%bb%a3%e7%a0%81%ef%bc%9f/

在开盘前算出一个价格，如果高于这个价格就卖出，低于3%以上就买入，比如周日我关注万科，我打算的数字是10，
如果万科价格是9.7我就买入，涨到10我就卖出。周一晚上我算出来12，如果周二价格是12*0.97=11.64我就买入

"""


# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.stock = "万科A"
    # 实时打印日志
    logger.info("Interested at stock: " + str(context.stock))
    # 判断当日是否已经买过或卖出了
    context.fired = False


# before_trading此函数会在每天交易开始前被调用，当天只会被调用一次
def before_trading(context):
    # 通过 history API 以及 只有1天来拿到前一天的历史收盘价
    hist_series = history_bars('万科A', 1, '1d', 'close')

    # 如果不清楚怎么使用的话，打印总是好的。这里返回的hist_series是一个series的类型，存储的是收盘价
    logger.info(str(hist_series))

    # 唯一的一个数据就是昨天的收盘价。
    yesterday_close = hist_series[0]

    # 利用context来储存一个全局变量 - 买入或卖出信号，这个信号由下面的逻辑来决定. 每天开盘前初始化变成‘’
    context.signal = ''

    # 将今日的操作重置为False
    context.fired = False

    # 假设计算出来的一个神奇数字是7.5, 那么如果低于3%以上就买入，高于7.5这个价格就卖出。
    # 您可以任意修改这个数值或者通过一些复杂的公式来计算出来这个神奇数字
    magic_number = 7.5
    if yesterday_close <= magic_number * 0.97:
        context.signal = 'buy'
    elif yesterday_close > magic_number:
        context.signal = 'sell'

    # 保持良好的习惯继续打印吧：
    if context.signal != '':
        logger.info('获得调仓信号： ' + context.signal)


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑

    # 如果您的策略今天没有下过单 （便于和分钟回测进行兼容）。
    if not context.fired:
        if context.signal == 'buy':
            # 0.99 表示用现有资金 99% 全部买入，留一部分给手续费
            order_target_percent(context.stock, 0.99)

            # 今天已经调仓买入了，不再操作
            context.fired = True
        elif context.signal == 'sell':
            # 设置成0就是清仓全部卖出了
            order_target_percent(context.stock, 0)

            # 今天已经调仓卖出了，不再操作
            context.fired = True


CONFIG = {
    "base": {
        "start_date": "20130901",
        "end_date": "20150901",
        "frequency": "1d",
        "benchmark": "000300.XSHG",
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
            # "matching_type": "last"
        },
    }
}

if __name__ == "__main__":
    from rqalpha import run_func
    run_func(init=init, before_trading=before_trading, handle_bar=handle_bar, config=CONFIG)
