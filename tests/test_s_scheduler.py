from rqalpha.apis import *


def init(context):
    scheduler.run_weekly(rebalance, 1, time_rule=market_open(0, 0))


def rebalance(context, bar_dict):
    stock = "000001.XSHE"
    if context.portfolio.positions[stock].quantity == 0:
        order_target_percent(stock, 1)
    else:
        order_target_percent(stock, 0)


CONFIG = {
    "base": {
        "start_date": "20180901",
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

if __name__ == "__main__":
    from rqalpha import run_func
    run_func(init=init, config=CONFIG)
