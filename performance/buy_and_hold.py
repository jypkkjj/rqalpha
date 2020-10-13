# 首先策略引入了RQAlpha的框架依赖，这是所有策略必须具备的。
from rqalpha.api import *

# 在这个方法中编写任何的初始化逻辑。context对象是由引擎构建并传入的，这个对象内涵了关于整个策略的信息，
# 这个对象也会出现在其他回调中，使用同一个实例。
def init(context):
    # 在这里定义了一个类似“全局变量”的变量。因为这个context对象实例会出现在别的回调中，因此在别的函数中
    # 也可以引用context.s1这个变量
    context.s1 = "000001.XSHE"

    # 告诉引擎该策略的股票池包含了什么股票，在这里股票池只有“平安银行”一个，您还可以传入一个列表或一个
    # 指数代码
    update_universe(context.s1)

    # 创建一个变量，用来判断是否已经执行过买入操作。因为行情会不断触发回调，因此需要策略自行判断是否
    # 已经买入过，而不是在每一次行情触发时都执行买入
    context.fired = False

    # 日志会直接打印在命令行（标准输出）中，您可以通过将输出流转发到文件的方式将日志保存下来。
    logger.info("RunInfo: {}".format(context.run_info))


# 这个回调模拟的是每个交易日开盘前希望执行的一些操作，例如对昨天收盘后的情况做一些处理来指导今天的交易，
# 但是在我们这个很简单的策略中并不需要这一回调，可以略过。
def before_trading(context):
    pass


# 这是前面提到的行情处理回调，也是整个策略的核心部分。行情是以K线的方式传入的，每当策略收到一个新的行情
# （在回测的情况下，就是下一个时间单位的K线准备好）时，这个函数就会被触发一次。
# 除了context变量之外，bar_dict就是含有行情信息的一个字典结构，它的key是合约代码，值是引擎内定义的
# Bar结构，包含了常见的开盘价、收盘价、最高最低价等信息，具体含义可以参考下面的链接：
# https://www.ricequant.com/doc/api/python/chn#object-bar
def handle_bar(context, bar_dict):

    # 这里就是策略逻辑的主体了。
    # 我们先判断买入的逻辑是否已经触发过，如果没有触发过，说明是第一次收到行情，那么就进行买入
    # 如果已经触发过，则什么也不做。
    if not context.fired:
        # order_percent并且传入1代表买入该股票并且使其占有投资组合的100%
        logger.info("order_percent:{}".format(order_percent(context.s1, 1)))

        # 注意将代表是否买入过的变量设为True，确保只执行一次买入操作
        context.fired = True


# 类似前面的before_trading，这个回调函数模拟了每个交易日收盘后需要进行的一些处理。
# 在这个策略中并不需要做任何处理，因此直接略过了。
def after_trading(context):
    pass

CONFIG = {
    "base": {
        "start_date": "20180901",
        "end_date": "20190901",
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
    run_func(init=init, handle_bar=handle_bar, config=CONFIG)
