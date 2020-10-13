# -*- coding: utf-8 -*-

import six
import tushare as ts
from datetime import date
import pandas as pd
from dateutil.relativedelta import relativedelta
from rqalpha.data.base_data_source import BaseDataSource
from rqalpha.utils.logger import system_log
from rqalpha.mod.rqalpha_mod_tushare_source.utils.instrument import ricequant_to_tushare, tushare_to_ricequant

map_adjust_type = {
    "pre": "qfq",  # 前复权
    "post": "hfq",  # 后复权
    "none": "None"
}


class TushareKDataSource(BaseDataSource):

    def __init__(self, path, token, max_workers=5):
        super(TushareKDataSource, self).__init__(path)
        self._pro = ts.pro_api(token)
        self._max_workers = max_workers

    @staticmethod
    def get_tushare_k_data(instrument, start_dt, end_dt):

        # 获取order_book_id 将其转成tushare 所能识别的 code
        order_book_id = instrument.order_book_id
        code = order_book_id.split(".")[0]

        if instrument.type == 'CS':
            index = False
        elif instrument.type == 'INDX':
            index = True
        else:
            return None
        """
        code: 证券代码：支持沪深A、B股,支持全部指数,支持ETF基金 
        ktype: 数据类型：默认为D日线数据,D=日k线 W=周 M=月 ,5=5分钟 15=15分钟,30=30分钟 60=60分钟
        autype: 复权类型：qfq-前复权 hfq-后复权 None-不复权，默认为qfq
        index: 是否为指数：默认为False,设定为True时认为code为指数代码
        start: 开始日期 format：YYYY-MM-DD 为空时取当前日期
        end:
        """
        return ts.get_k_data(code, index=index, start=start_dt.strftime('%Y-%m-%d'), end=end_dt.strftime('%Y-%m-%d'))



    # def get_pro_bar(self, ts_code, adj, start_date, end_date):
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
    #         futures = [executor.submit(evaluate_item, a=1, b=2, c=3) for item in number_list]
    #         for future in concurrent.futures.as_completed(futures):
    #             print(future.result())

    def get_bar(self, instrument, dt, frequency):
        if frequency != '1d':
            return super(TushareKDataSource, self).get_bar(instrument, dt, frequency)

        bar_data = self.get_tushare_k_data(instrument, dt, dt)

        if bar_data is None or bar_data.empty:
            system_log.warn("tuahre get_tushare_k_data return date is None")
            return super(TushareKDataSource, self).get_bar(instrument, dt, frequency)
        else:
            return bar_data.iloc[0].to_dict()

    def history_bars(self, instrument, bar_count, frequency, fields, dt, skip_suspended=True, include_now=False,
                     adjust_type='pre', adjust_orig=None):
        if frequency != '1d' or not skip_suspended:
            return super(TushareKDataSource, self).history_bars(instrument, bar_count, frequency, fields, dt,
                                                                skip_suspended)

        start_dt_loc = self.get_trading_calendar().get_loc(
            dt.replace(hour=0, minute=0, second=0, microsecond=0)) - bar_count + 1
        start_dt = self.get_trading_calendar()[start_dt_loc]

        bar_data = self.get_tushare_k_data(instrument, start_dt, dt)

        if bar_data is None or bar_data.empty:
            system_log.warn("tuahre get_tushare_k_data return date is None")
            return super(TushareKDataSource, self).get_bar(instrument, dt, frequency)
        else:
            if isinstance(fields, six.string_types) and fields in bar_data.columns:
                return bar_data[fields].values
            fields = [fields]
            fields = [field for field in fields if field in bar_data.columns]

            # return bar_data[fields].as_matrix()
            return bar_data[fields]

    def get_price(self, instrument, start_date, end_date, frequency='1d', fields=None, adjust_type='pre',
                  skip_suspended=False):
        """
        :param instrument:
        :param start_date: 开始日期 (格式：YYYYMMDD)
        :param end_date:  结束日期 (格式：YYYYMMDD)
        :param frequency: 1MIN表示1分钟（1/5/15/30/60分钟） D日线 ，默认D
        :param fields:
        :param adjust_type: 复权类型(只针对股票)：None未复权 qfq前复权 hfq后复权 , 默认None
        :param skip_suspended:
        :return:
        """
        # 获取order_book_id 将其转成tushare 所能识别的 code
        # order_book_id = ricequant_to_tushare(instrument.order_book_id)
        order_book_id = ricequant_to_tushare(instrument)

        # adj:  None未复权 qfq前复权 hfq后复权 , 默认None
        # asset: 资产类别：E股票 I沪深指数 C数字货币 FT期货 FD基金 O期权，默认E
        adj = map_adjust_type[adjust_type]
        start_date = '{}'.format(start_date).replace("-", "")
        end_date = '{}'.format(end_date).replace("-", "")
        bar_data = ts.pro_bar(pro_api=self._pro, ts_code=order_book_id, adj=adjust_type, start_date=start_date,
                              end_date=end_date)

        if bar_data is None or bar_data.empty:
            system_log.error("tuahre get_tushare_k_data return date is None")
        else:
            bar_data['trade_date'] = pd.to_datetime(bar_data['trade_date'])
            bar_data.set_index(bar_data['trade_date'], inplace=True)
            bar_data.rename(columns={'vol': 'volume'}, inplace=True)
            bar_data.sort_index(inplace=True)
            if isinstance(fields, six.string_types) and fields in bar_data.columns:
                return bar_data[fields].values
            # fields = [fields]
            fields = [field for field in fields if field in bar_data.columns]
            # return bar_data[fields].values
            return bar_data[fields]

    def available_data_range(self, frequency):
        return date(2005, 1, 1), date.today() - relativedelta(days=1)


if __name__ == "__main__":
    """
    get_k_data 接口测试
    文档：
    https://mp.weixin.qq.com/s?__biz=MzAwOTgzMDk5Ng==&mid=2650833972&idx=1&sn=4de9f9ee81bc8bf85d1e0a4a8f79b0de&chksm=80adb30fb7da3a19817c72ff6f715ee91d6e342eb0402e860e171993bb0293bc4097e2dc4fe9&mpshare=1&scene=1&srcid=1106BPAdPiPCnj6m2Xyt5p2M
    """
    # code = '002743'
    # index = False
    # start_dt = '2018-02-01'
    # end_dt = '2018-02-28'
    # result = ts.get_k_data(code, index=index, start=start_dt, end=end_dt)
    # print(result)

    # https://python-parallel-programmning-cookbook.readthedocs.io/zh_CN/latest/chapter4/02_Using_the_concurrent.futures_Python_modules.html
    import concurrent.futures

    number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


    def evaluate_item(a, b, c):
        return a + b + c
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(evaluate_item, a=1, b=2, c=3) for item in number_list]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
