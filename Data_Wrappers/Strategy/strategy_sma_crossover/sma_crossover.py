from Data_Wrappers.Strategy.strategy_wrapper import strategy_wrapper
from Data_Wrappers.Indicators.EMA import EMA
import pandas as pd
import os
import uuid
from Util import Util, interval_enum, trend_type
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from Data_Wrappers.Trend.Trend import Trend, trend_term


class sma_crossover(strategy_wrapper):
    def __init__(self):
        self.share_name = ['HCLTECH-EQ']
        self.time_interval = [interval_enum.ONE_DAY]
        broker = 'angle'
        self.indicators = [EMA(interval=23, on='close'), EMA(interval=53, on='close'), EMA(interval=13, on='close')]
        self.trend = Trend('HCLTECH-EQ', trend_term.MID_TERM, interval_enum.ONE_DAY)
        super().__init__(share_name=self.share_name, time_interval=self.time_interval, broker=broker,
                         indicators=self.indicators, start_date=datetime.today()-relativedelta(years=9), end_date=datetime.today())

    def backtest_strategy(self):

        small_sma_name = 'ema' + '_' + str(self.indicators[0].interval)
        higher_sma_name = 'ema' + '_' + str(self.indicators[1].interval)
        exit_sma_name = 'ema' + '_' + str(self.indicators[2].interval)
        df = pd.DataFrame(
            columns=['symbol', 'trade_type', 'quantity', 'price', 'order_execution_time', 'system_trade_id',
                     'interval','stop_loss'])
        data = self.data_list[0]
        watch = False
        stoploss = 0
        in_trade = False
        trade_id = ''
        quantity = 0
        buy_price = 0
        symbol = self.share_name[0]
        interval = self.time_interval[0]
        half_book = False
        for ind in data.index:
            small_sma = data[small_sma_name][ind]
            higher_sma = data[higher_sma_name][ind]
            exit_sma = data[exit_sma_name][ind]
            if watch == False:
                if higher_sma > 0 and small_sma > 0:
                    if data[small_sma_name][ind - 1] < data[higher_sma_name][ind - 1] and small_sma > higher_sma:
                        if self.trend.get_trend(data['datetime'][ind]) in [trend_type.UP, trend_type.STRONG_UP]:
                            watch = True
                            stop_idx = ind-1
                            while True:
                                low_val = data['low'][stop_idx]
                                close = data['close'][stop_idx]
                                small_sma_stop = data[small_sma_name][stop_idx]
                                higher_sma_stop = data[higher_sma_name][stop_idx]
                                if low_val < small_sma_stop and low_val < higher_sma_stop and close < small_sma_stop and close < higher_sma_stop:
                                    stoploss = low_val
                                    break
                                else:
                                    stop_idx = stop_idx - 1
            else:
                low = data['low'][ind]
                high = data['high'][ind]
                close = data['close'][ind]
                if in_trade == False:
                    if small_sma > low and close > small_sma > higher_sma:
                        in_trade = True
                        trade_id = uuid.uuid1()
                        quantity = 20
                        buy_price = close
                        order_execution_time = data['datetime'][ind]
                        buy_df = {'symbol': symbol, 'trade_type': 'buy', 'quantity': quantity, 'price': buy_price,
                               'order_execution_time': order_execution_time
                            , 'system_trade_id': trade_id, 'interval': interval.name, 'stop_loss':stoploss}
                        df = df.append(buy_df, ignore_index=True)
                else:
                    target = buy_price + (buy_price - stoploss)
                    if low <= target <= high and half_book == False:
                        sell_df = {'symbol': symbol, 'trade_type': 'sell', 'quantity': int(quantity/2), 'price': target,
                                  'order_execution_time': data['datetime'][ind]
                            , 'system_trade_id': trade_id, 'interval': interval.name, 'stop_loss':stoploss}
                        quantity = quantity - int(quantity/2)
                        df = df.append(sell_df, ignore_index=True)
                        half_book = True

                    if (close <= stoploss) or (exit_sma < higher_sma):
                        sell_df = {'symbol': symbol, 'trade_type': 'sell', 'quantity': quantity,
                                   'price': close,
                                   'order_execution_time': data['datetime'][ind]
                            , 'system_trade_id': trade_id, 'interval': interval.name,'stop_loss':stoploss}
                        in_trade = False
                        watch = False
                        half_book = False
                        df = df.append(sell_df, ignore_index=True)

        Util.convert_dataframe_csv(df, 'trades/' + self.__class__.__name__, symbol + '_' + interval.name)




    def buy_share(self):
        super().buy_share()

    def sell_share(self):
        super().sell_share()
