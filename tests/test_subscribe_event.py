# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_subscribe_event
   Description :
   Author :        mixbe
   date：          2020/10/14
-------------------------------------------------
   Change Activity:
                   2020/10/14:
-------------------------------------------------
"""


def init(context):
    # 注册成交事件
    subscribe_event(EVENT.TRADE, on_trade)
    # 注册订单成功创建事件
    subscribe_event(EVENT.ORDER_CREATION_PASS, on_order_created)
    context.count = 0
    context.s1 = '000001.XSHE'

# 回调函数定义中需要包含 context, event 参数
def on_trade(context, event):
    # 获取成交信息
    trade = event.trade
    if trade.order_book_id == context.s1:
    	print(trade)

# 回调函数定义中需要包含 event 这一参数
def on_order_created(context, event):
    # 获取订单信息
    order = event.order
    print(order)

def handle_bar(context, bar_dict):
    px = bar_dict['000001.XSHE'].last + 0.2
    if context.count == 0:
        # 订单创建, 并使用关键字 context 保存全局变量
        submit_order(context.s1, amount=100, side=SIDE.BUY, price=px)
        context.count += 1

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