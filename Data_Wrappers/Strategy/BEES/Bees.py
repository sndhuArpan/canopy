import uuid
from datetime import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
from Data_Wrappers.Strategy.strategy_wrapper import strategy_wrapper
from Util import interval_enum, Util
import math
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema, find_peaks
from zigzag import *
import matplotlib.pyplot as plt


class Bees(strategy_wrapper):
    def __init__(self):
        self.amount_intial = 100000
        self.amount = 100000
        self.book_percent = 3
        self.share_name = ['ITC-EQ']
        self.amount_per_percent = 10000
        self.avg_buy = 0
        self.buy_quantity = 0
        self.time_interval = [interval_enum.ONE_DAY]
        broker = 'angle'
        self.start_date = datetime.today() - relativedelta(years=2)
        self.end_date = datetime.today()
        super().__init__(share_name=self.share_name, time_interval=self.time_interval, broker=broker,
                         start_date=self.start_date, end_date=datetime.today())

    def backtest_strategy(self):
        self.df = Util.get_trade_sheet_df()
        trade_id = ''
        quantity = 0
        in_trade = False
        self.insufficant_amount = 0
        self.number_trades = 0
        previous_buy = 0
        buy_idx = []
        sell_idx = []

        for share in self.share_name:
            self.bee_data = self.data_list.get(share + '_' + self.time_interval[0].name)
            self.bee_data.index = np.arange(0, len(self.bee_data))
            pivots = peak_valley_pivots(self.bee_data['close'].values, 0.015, -0.015)
            ts_pivots = pd.Series(self.bee_data['close'], index=self.bee_data['close'].index)
            ts_pivots = ts_pivots[pivots != 0]
            # self.bee_data['close'].plot()
            ts_pivots.plot(style='g-o');
            # for ind in self.bee_data.index:
            #     if ind < 10:
            #         continue
            #     pivots = peak_valley_pivots(self.bee_data['close'][0:ind + 1].values, 0.025, -0.025)
            #     ts_pivots = pd.Series(self.bee_data['close'][0:ind + 1], index=self.bee_data['close'][0:ind + 1].index)
            #     ts_pivots_low = ts_pivots[pivots == -1]
            #     ts_pivots_high = ts_pivots[pivots == 1]
            #     close_price = self.bee_data['close'][ind]
            #     if ts_pivots_low.size >= 3 and ts_pivots_high.size >= 1 and in_trade == False:
            #
            #         if close_price > ts_pivots_high.iloc[-1]:
            #             buy_price = close_price
            #             trade_id = uuid.uuid4()
            #             quantity = math.ceil(self.amount / buy_price)
            #             in_trade = True
            #             stoploss = ts_pivots_low.iloc[ts_pivots_low.size - 2]
            #             buy_df = dict(symbol=share, trade_type='buy', quantity=quantity, price=buy_price,
            #                           order_execution_time=self.bee_data['datetime'][ind], system_trade_id=trade_id,
            #                           interval=self.time_interval[0].name, stop_loss=stoploss, instrument_type='equity',
            #                           broker='angel')
            #             buy_idx.append(ind)
            #             self.amount = self.amount - quantity * close_price
            #             self.df = self.df.append(buy_df, ignore_index=True)
            #
            #     if in_trade:
            #         if close_price <= stoploss:
            #             in_trade = False
            #             sell_idx.append(ind)
            #             sell_df = dict(symbol=share, trade_type='sell', quantity=quantity, price=close_price,
            #                            order_execution_time=self.bee_data['datetime'][ind], system_trade_id=trade_id,
            #                            interval=self.time_interval[0].name, stop_loss=stoploss,
            #                            instrument_type='equity',
            #                            broker='angel')
            #             self.df = self.df.append(sell_df, ignore_index=True)
            #             self.amount = self.amount + quantity * close_price
            #         else:
            #             if close_price < ts_pivots_low.iloc[ts_pivots_low.size - 2]:
            #                 in_trade = False
            #                 sell_idx.append(ind)
            #                 sell_df = dict(symbol=share, trade_type='sell', quantity=quantity, price=close_price,
            #                                order_execution_time=self.bee_data['datetime'][ind], system_trade_id=trade_id,
            #                                interval=self.time_interval[0].name, stop_loss=stoploss,
            #                                instrument_type='equity',
            #                                broker='angel')
            #                 self.amount = self.amount + quantity * close_price
            #                 self.df = self.df.append(sell_df, ignore_index=True)
            # self.bee_data['close'].plot()
            # self.bee_data['close'][buy_idx].plot(color='green', marker='o', linewidth=0)
            # self.bee_data['close'][sell_idx].plot(color='red', marker='o', linewidth=0)
            # Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
            #                            self.__class__.__name__)
            plt.show()

            # # maxima = self.bee_data['close'][argrelextrema(np.array(self.bee_data['close']), np.greater)[0]]
            # # minima = self.bee_data['close'][argrelextrema(np.array(self.bee_data['close']), np.less)[0]]
            # for ind in self.bee_data.index:
            #     if ind < 10:
            #         continue
            #     else:
            #         peeks = self.bee_data['close'][find_peaks(self.bee_data['close'][0:ind],distance=10)[0]]
            #         close_price = self.bee_data['close'][ind]
            #         if (((peeks.iloc[-1] - close_price)/close_price)*100 > 2) or in_trade:
            #             percent_change = ((close_price - self.bee_data['close'][ind - 1]) / self.bee_data['close'][
            #                 ind - 1]) * 100
            #             if percent_change <= 0 and (previous_buy > close_price or in_trade == False):
            #                 amount_to_invest = abs(self.amount_per_percent * percent_change)
            #                 if amount_to_invest < self.amount:
            #                     if not in_trade:
            #                         in_trade = True
            #                         trade_id = uuid.uuid4()
            #                         previous_buy = peeks.iloc[-1]
            #                     quantity = math.ceil(amount_to_invest / close_price)
            #                     buy_df = {'symbol': share, 'trade_type': 'buy', 'quantity': quantity,
            #                               'price': close_price,
            #                               'order_execution_time': self.bee_data['datetime'][ind]
            #                         , 'system_trade_id': trade_id, 'interval': self.time_interval[0].name,
            #                               'stop_loss': 0, 'instrument_type': 'equity', 'broker': 'angel','avg_buy':''}
            #
            #                     self.df = self.df.append(buy_df, ignore_index=True)
            #                     self.avg_buy = (self.avg_buy * self.buy_quantity + close_price * quantity)
            #                     self.buy_quantity = self.buy_quantity + quantity
            #                     self.avg_buy = self.avg_buy / self.buy_quantity
            #                     self.amount = self.amount - quantity * close_price
            #                 else:
            #                     self.insufficant_amount = self.insufficant_amount + 1
            #
            #         if self.avg_buy > 0:
            #             self.current_profit = ((close_price - self.avg_buy) / self.avg_buy) * 100
            #             if self.current_profit >= self.book_percent:
            #                 in_trade = False
            #                 self.amount = self.amount + self.buy_quantity*close_price
            #                 sell_df = {'symbol': share, 'trade_type': 'sell', 'quantity': self.buy_quantity,
            #                            'price': close_price,
            #                            'order_execution_time': self.bee_data['datetime'][ind]
            #                     , 'system_trade_id': trade_id, 'interval': self.time_interval[0].name,
            #                            'stop_loss': 0, 'instrument_type': 'equity', 'broker': 'angel','avg_buy':self.avg_buy}
            #                 self.df = self.df.append(sell_df, ignore_index=True)
            #                 self.buy_quantity = 0
            #                 self.avg_buy = 0
            #                 self.number_trades = self.number_trades+1
            #                 previous_buy = 0
            # Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
            #                            self.__class__.__name__)
            # print(self.insufficant_amount)
            # print(self.number_trades)
            # print(self.amount)
            # print(self.amount + self.buy_quantity*self.avg_buy)

    def buy_share(self):
        pass

    def sell_share(self):
        pass
