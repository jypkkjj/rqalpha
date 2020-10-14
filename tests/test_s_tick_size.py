SLIPPAGE = 10
price = 0
stock = "000001.XSHE"


def init(context):
    context.count = 0
    context.tick_size = instruments(stock).tick_size()
    subscribe_event(EVENT.TRADE, on_trade)


def on_trade(context, event):
    global price
    trade = event.trade
    #assert trade.last_price == price + context.tick_size * SLIPPAGE


def before_trading(context):
    pass


def handle_bar(context, bar_dict):
    global price
    if context.count == 1:
        price = bar_dict[stock].close
        order_shares(stock, 100)
    context.count += 1


def after_trading(context):
    pass


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
    run_func(init=init, handle_bar=handle_bar, config=CONFIG)
