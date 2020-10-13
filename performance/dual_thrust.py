

from rqalpha import run_func


# 参考 https://blog.ricequant.com/2020/08/07/dual-thrust-%e4%ba%a4%e6%98%93%e7%ad%96%e7%95%a5/

def init(context):
    context.stocks = ['中证500']
    update_universe(context.stocks)


def handle_bar(context, bar_dict):
    # stocknum = 50
    his = history_bars('000001.XSHE',10, '1d', 'close')

    # print(his)

    if his[9] / his[8] < 0.97:
        if len(context.portfolio.positions) > 0:
            for stock in context.portfolio.positions.keys():
                order_target_percent(stock, 0)
        return

    # 分配资金
    # if len(context.portfolio.positions) < stocknum:
    # Num = stocknum - len(context.portfolio.positions)
    # Cash = context.portfolio.cash/Num
    # else:
    # Cash = context.portfolio.cash

    # Buy
    for stock in context.stocks:
        # 求出持有该股票的仓位，买入没有持仓并符合条件股票
        position = context.portfolio.positions[stock].quantity
        print(stock)
        # print(position)
        if position < 100:
            High = history_bars(stock, 3, '1d', 'high')
            Low = history_bars(stock, 3, '1d', 'low')
            Close = history_bars(stock, 3, '1d', 'close')
            Open = history_bars(stock, 3, '1d', 'open')

            # logger.info(High)

            HH = max(High[:2])
            LC = min(Close[:2])
            HC = max(Close[:2])
            LL = min(Low[:2])
            Openprice = Open[2]
            # logger.info(HH)
            # print(LC)
            # print(HC)
            # print(LL)
            # print(Openprice)

            # 使用第n-1日的收盘价作为当前价
            current_price = Close[2]

            print(current_price, 'price')

            Range = max((HH - LC), (HC - LL))
            K1 = 0.9
            BuyLine = Openprice + K1 * Range
            # print(BuyLine,'buyline')
            if current_price > BuyLine:
                order_target_percent(stock, 1)

    # Sell
    for stock in context.portfolio.positions.keys():
        hist = history_bars(stock, 3, '1d', 'close')
        case1 = (1 - hist[2] / hist[0]) >= 0.06
        case2 = hist[1] / hist[0] <= 0.92
        if case1 or case2:
            order_target_percent(stock, 0)

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
    run_func(init=init, handle_bar=handle_bar, config=CONFIG)