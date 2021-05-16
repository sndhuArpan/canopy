from Data_Wrappers.Strategy.strategy_wrapper import strategy_wrapper
from Data_Wrappers.Indicators.EMA import EMA
import pandas as pd
import os
import uuid
from Util import Util, interval_enum, trend_type
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from Data_Wrappers.Trend.Trend import Trend, trend_term
import numpy as np


class basic_trend(strategy_wrapper):
    def __init__(self):
        self.amount = 100000
        self.share_name = ['HCLTECH-EQ', 'TCS-EQ', 'SRF-EQ']
        self.amount_per_share = int(self.amount/self.share_name.__len__())
        self.time_interval = [interval_enum.ONE_DAY, interval_enum.FIFTEEN_MINUTE]
        broker = 'angle'
        self.trend = Trend(trend_term.SHORT_TERM, interval_enum.ONE_DAY)
        self.start_date = datetime.today()-relativedelta(years=9)
        self.end_date = datetime.today()
        super().__init__(share_name=self.share_name, time_interval=self.time_interval, broker=broker, start_date=datetime.today()-relativedelta(years=9), end_date=datetime.today())

    def backtest_strategy(self):
        intial_date = self.start_date
        self.data_trend = []
        self.data_trade = []
        self.trade_status = []
        self.df = Util.get_trade_sheet_df()
        max_index = 0
        share_symbol = []
        for share in self.share_name:
            trend_data = self.data_list.get(share+'_'+self.time_interval[0].name)
            trade_data = self.data_list.get(share + '_' + self.time_interval[1].name)
            first_date = trade_data['datetime'][0]
            convert_date = Util.get_hour_start_date(Util.convert_str_date(first_date),self.time_interval[0])
            convert_date = convert_date.strftime("%Y-%m-%dT%H:%M:%S")
            index = trend_data.index[trend_data['datetime'] == convert_date].tolist()[0]
            trend_data = trend_data[index - trend_data.index[0]:trend_data.index[-1]]
            trend_data.index = np.arange(0, len(trend_data))
            if max_index < len(trend_data):
                max_index = len(trend_data)
            self.data_trend.append(trend_data)
            self.data_trade.append(trade_data)
            share_symbol.append(Util.get_symbol_token(share))

        for ind in range(max_index-1):
            for i, data in enumerate(self.data_trend):
                if ind in data['datetime'].index:
                    trend_date = data['datetime'][ind]
                    print(trend_date)
                    share_trend = self.trend.get_trend(trend_date, share_symbol=share_symbol[i])
                    if share_trend == trend_type.STRONG_UP:
                        if ind + 1 in data['datetime'].index:
                            self.run_track_trade(i, data['datetime'][ind+1])

        Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__, self.__class__.__name__)

    def run_track_trade(self, i, trade_date):
        start_time = Util.get_hour_start_date(Util.convert_str_date(trade_date),self.time_interval[1])
        start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        data_trade = self.data_trade[i]
        index_list = data_trade.index[data_trade['datetime'] == start_time].tolist()
        if index_list:
            index = index_list[0]
        else:
            return
        data = data_trade.iloc[[index]]
        quantity = 0
        trade_id = ''
        target = 0
        in_trade = False
        if (data['close'] > data['open'])[index]:
            stoploss = data['low'][index]
            buy_price = data_trade['open'][index+1]
            quantity = int(self.amount_per_share/buy_price)
            trade_id = uuid.uuid1()
            target = buy_price + (2*(buy_price-stoploss))
            buy_df = {'symbol': self.share_name[i], 'trade_type': 'buy', 'quantity': quantity, 'price': buy_price,
                      'order_execution_time': data_trade['datetime'][index+1]
                , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name, 'stop_loss': stoploss}
            self.df = self.df.append(buy_df, ignore_index=True)
            in_trade = True

        if in_trade:
            candles_in_days = Util.get_candles_per_day(self.time_interval[1])
            for candle_idx in range(candles_in_days-1):
                candle_low = data_trade['low'][index+candle_idx+1]
                candle_high = data_trade['high'][index+candle_idx+1]
                if stoploss >= candle_low:
                    sell_df = {'symbol': self.share_name[i], 'trade_type': 'sell', 'quantity': quantity,
                              'price': stoploss,
                              'order_execution_time': data_trade['datetime'][index+ candle_idx+ 1]
                        , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name, 'stop_loss': stoploss}
                    in_trade = False
                    break
                if candle_low <= target <= candle_high:
                    sell_df = {'symbol': self.share_name[i], 'trade_type': 'sell', 'quantity': quantity,
                               'price': target,
                               'order_execution_time': data_trade['datetime'][index + candle_idx + 1]
                        , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name, 'stop_loss': stoploss}
                    in_trade = False
                    break
            if in_trade:
                sell_df = {'symbol': self.share_name[i], 'trade_type': 'sell', 'quantity': quantity,
                           'price': data_trade['open'][index+candles_in_days-1],
                           'order_execution_time': data_trade['datetime'][index+candles_in_days-1]
                    , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name, 'stop_loss': stoploss}
                in_trade = False
            self.df = self.df.append(sell_df, ignore_index=True)



    def buy_share(self):
        super().buy_share()

    def sell_share(self):
        super().sell_share()
