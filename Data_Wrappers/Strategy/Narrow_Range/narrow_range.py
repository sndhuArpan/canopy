import uuid
from datetime import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
from Data_Wrappers.Strategy.strategy_wrapper import strategy_wrapper
from Util import interval_enum, Util
import math

class narrow_range(strategy_wrapper):
    def __init__(self):
        self.amount = 100000
        self.narrow_range = 4
        # self.share_name = ['ADANIPORTS-EQ', 'ASIANPAINT-EQ', 'AXISBANK-EQ', 'BAJFINANCE-EQ', 'BAJAJFINSV-EQ',
        #                    'BPCL-EQ', 'BHARTIARTL-EQ', 'CIPLA-EQ', 'COALINDIA-EQ',
        #                    'DRREDDY-EQ', 'EICHERMOT-EQ', 'GAIL-EQ', 'GRASIM-EQ', 'HCLTECH-EQ',
        #                    'HDFCBANK-EQ', 'HEROMOTOCO-EQ', 'HINDALCO-EQ', 'HINDPETRO-EQ', 'HINDUNILVR-EQ',
        #                    'HDFC-EQ', 'ITC-EQ', 'ICICIBANK-EQ', 'IOC-EQ', 'INDUSINDBK-EQ',
        #                    'INFY-EQ', 'JSWSTEEL-EQ', 'KOTAKBANK-EQ', 'LT-EQ', 'MARUTI-EQ',
        #                    'NTPC-EQ', 'ONGC-EQ', 'POWERGRID-EQ', 'RELIANCE-EQ',
        #                    'SUNPHARMA-EQ', 'TCS-EQ', 'TATAMOTORS-EQ', 'TATASTEEL-EQ', 'TECHM-EQ',
        #                    'TITAN-EQ', 'UPL-EQ', 'ULTRACEMCO-EQ', 'VEDL-EQ', 'WIPRO-EQ',
        #                    'YESBANK-EQ', 'ZEEL-EQ']
        self.share_name = ['NIFTY','NIFTYBEES-EQ']

        self.amount_per_share = 20000
        self.time_interval = [interval_enum.ONE_DAY]
        broker = 'angle'
        self.start_date = datetime.today() - relativedelta(years=9)
        self.end_date = datetime.today()
        super().__init__(share_name=self.share_name, time_interval=self.time_interval, broker=broker,
                         start_date=self.start_date, end_date=datetime.today())

    # initail without trailing
    # def backtest_strategy(self):
    #     self.df = Util.get_trade_sheet_df()
    #     for share in self.share_name:
    #         print(share)
    #         self.range_data = self.data_list.get(share + '_' + self.time_interval[0].name)
    #         trade_data = self.data_list.get(share + '_' + self.time_interval[1].name)
    #         trade_data.index = np.arange(0, len(trade_data))
    #         first_date = trade_data['datetime'][0]
    #         convert_date = self.get_str_date(first_date, self.time_interval[0])
    #         index = self.range_data.index[self.range_data['datetime'] == convert_date].tolist()[0]
    #         self.range_data = self.range_data[index - self.range_data.index[0]:self.range_data.index[-1]]
    #         self.range_data.index = np.arange(0, len(self.range_data))
    #         watch = False
    #         in_trade = False
    #         cnadle_in_trade_interval = Util.get_candles_per_day(self.time_interval[1])
    #         range_index = 3
    #         stoploss = 0
    #         target = 0
    #         trade_id = ''
    #         for ind in self.range_data.index:
    #             if not ind > range_index:
    #                 continue
    #             if not watch and not in_trade:
    #                 watch = self.is_narrow_range(ind)
    #                 continue
    #
    #             if watch:
    #                 trade_date = self.get_str_date(self.range_data['datetime'][ind], self.time_interval[1])
    #                 try:
    #                     index = trade_data.index[trade_data['datetime'] == trade_date].tolist()[0]
    #                 except:
    #                     watch = False
    #                     continue
    #                 in_loop = True
    #                 while in_loop:
    #                     if not index + (cnadle_in_trade_interval * self.narrow_range) - 1 in trade_data.index:
    #                         index = trade_data.index[-1]
    #                         watch = False
    #                         break
    #                     if self.high_range < trade_data['close'][index]:
    #                         break_out_idx = index
    #                         break_out_date = self.get_str_date(trade_data['datetime'][break_out_idx],
    #                                                            self.time_interval[0])
    #                         breakout_range_index = \
    #                         self.range_data.index[self.range_data['datetime'] == break_out_date].tolist()[0]
    #                         if self.range_data['low'][breakout_range_index] < self.range_data['low'][
    #                             breakout_range_index - 1]:
    #                             stoploss = self.range_data['low'][breakout_range_index]
    #                         else:
    #                             stoploss = self.range_data['low'][breakout_range_index - 1]
    #                         if trade_data['close'][break_out_idx] < trade_data['close'][break_out_idx + 1]:
    #                             buy_price = trade_data['close'][break_out_idx + 1]
    #                             target = buy_price + (self.high_range - self.low_range)
    #                             order_execution_time = trade_data['datetime'][break_out_idx + 1]
    #                             quantity = math.ceil(self.amount_per_share / buy_price)
    #                             trade_id = uuid.uuid4()
    #                             buy_df = {'symbol': share, 'trade_type': 'buy', 'quantity': quantity,
    #                                       'price': buy_price,
    #                                       'order_execution_time': order_execution_time
    #                                 , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name,
    #                                       'stop_loss': stoploss}
    #                             self.df = self.df.append(buy_df, ignore_index=True)
    #                             in_trade = True
    #                             watch = False
    #                             index = break_out_idx + 1
    #                             break
    #                         else:
    #                             for i in range((cnadle_in_trade_interval * self.narrow_range) - 1):
    #                                 index = index + 1
    #                                 if trade_data['low'][index] < self.high_range < trade_data['close'][index] and \
    #                                         trade_data['open'][index] < trade_data['close'][index]:
    #                                     buy_price = trade_data['close'][index]
    #                                     target = buy_price + (self.high_range - self.low_range)
    #                                     order_execution_time = trade_data['datetime'][index]
    #                                     quantity = math.ceil(self.amount_per_share / buy_price)
    #                                     trade_id = uuid.uuid4()
    #                                     buy_df = {'symbol': share, 'trade_type': 'buy', 'quantity': quantity,
    #                                               'price': buy_price,
    #                                               'order_execution_time': order_execution_time
    #                                         , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name,
    #                                               'stop_loss': stoploss}
    #                                     self.df = self.df.append(buy_df, ignore_index=True)
    #                                     in_trade = True
    #                                     watch = False
    #                                     break
    #                         watch = False
    #                         break
    #                     index = index + 1
    #                 range_date = self.get_str_date(trade_data['datetime'][index], self.time_interval[0])
    #                 range_index = self.range_data.index[self.range_data['datetime'] == range_date].tolist()[0]
    #
    #             else:
    #                 if in_trade:
    #                     if self.range_data['high'][ind] >= target:
    #                         in_trade = False
    #                         sell_df = {'symbol': share, 'trade_type': 'sell', 'quantity': quantity,
    #                                    'price': target,
    #                                    'order_execution_time': self.range_data['datetime'][ind]
    #                             , 'system_trade_id': trade_id, 'interval': self.time_interval[0].name,
    #                                    'stop_loss': stoploss}
    #                         self.df = self.df.append(sell_df, ignore_index=True)
    #                     else:
    #                         if self.range_data['low'][ind] <= stoploss:
    #                             in_trade = False
    #                             sell_df = {'symbol': share, 'trade_type': 'sell', 'quantity': quantity,
    #                                        'price': stoploss,
    #                                        'order_execution_time': self.range_data['datetime'][ind]
    #                                 , 'system_trade_id': trade_id, 'interval': self.time_interval[0].name,
    #                                        'stop_loss': stoploss}
    #                             self.df = self.df.append(sell_df, ignore_index=True)
    #
    #     Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
    #                                self.__class__.__name__ + '_' + str(self.narrow_range))

    def get_str_date(self, date, interval):
        convert_date = Util.get_hour_start_date(Util.convert_str_date(date), interval)
        convert_date = convert_date.strftime("%Y-%m-%dT%H:%M:%S")
        return convert_date

    def is_narrow_range(self, ind):
        narrow_range_idx = ind - self.narrow_range + 1
        if not narrow_range_idx in self.range_data['high'].index:
            return False

        self.high_range = self.range_data['high'][narrow_range_idx]
        self.low_range = self.range_data['low'][narrow_range_idx]
        for i in range(self.narrow_range - 1):
            current_candle_idx = narrow_range_idx + 1 + i
            in_range = False
            if self.low_range <= self.range_data['open'][current_candle_idx] <= self.high_range:
                if self.low_range <= self.range_data['close'][current_candle_idx] <= self.high_range:
                    if (self.high_range - self.low_range) >= (
                            self.range_data['high'][current_candle_idx] - self.range_data['low'][current_candle_idx]):
                        in_range = True
            if in_range:
                continue
            else:
                return False
        return True

    # with trailing stoploss after the target
    def backtest_strategy(self):
        self.df = Util.get_trade_sheet_df()
        for share in self.share_name:
            print(share)
            self.range_data = self.data_list.get(share + '_' + self.time_interval[0].name)
            trade_data = self.data_list.get(share + '_' + self.time_interval[1].name)
            trade_data.index = np.arange(0, len(trade_data))
            first_date = trade_data['datetime'][0]
            convert_date = self.get_str_date(first_date, self.time_interval[0])
            index = self.range_data.index[self.range_data['datetime'] == convert_date].tolist()[0]
            self.range_data = self.range_data[index - self.range_data.index[0]:self.range_data.index[-1]]
            self.range_data.index = np.arange(0, len(self.range_data))
            watch = False
            in_trade = False
            half_booked = False
            cnadle_in_trade_interval = Util.get_candles_per_day(self.time_interval[1])
            range_index = 3
            stoploss = 0
            stoploss_diff = 0
            target = 0
            trade_id = ''
            for ind in self.range_data.index:
                if not ind > range_index:
                    continue
                if not watch and not in_trade:
                    watch = self.is_narrow_range(ind)
                    continue

                if watch:
                    trade_date = self.get_str_date(self.range_data['datetime'][ind], self.time_interval[1])
                    try:
                        index = trade_data.index[trade_data['datetime'] == trade_date].tolist()[0]
                    except:
                        watch = False
                        continue
                    in_loop = True
                    while in_loop:
                        if not index + (cnadle_in_trade_interval * self.narrow_range) - 1 in trade_data.index:
                            index = trade_data.index[-1]
                            watch = False
                            break
                        if self.high_range < trade_data['close'][index]:
                            break_out_idx = index
                            break_out_date = self.get_str_date(trade_data['datetime'][break_out_idx],
                                                               self.time_interval[0])
                            breakout_range_index = \
                            self.range_data.index[self.range_data['datetime'] == break_out_date].tolist()[0]
                            if self.range_data['low'][breakout_range_index] < self.range_data['low'][
                                breakout_range_index - 1]:
                                stoploss = self.range_data['low'][breakout_range_index]
                            else:
                                stoploss = self.range_data['low'][breakout_range_index - 1]
                            if trade_data['close'][break_out_idx] < trade_data['close'][break_out_idx + 1]:
                                buy_price = trade_data['close'][break_out_idx + 1]
                                stoploss_diff = buy_price - stoploss
                                target = buy_price + (self.high_range - self.low_range)
                                order_execution_time = trade_data['datetime'][break_out_idx + 1]
                                quantity = math.ceil(self.amount_per_share / buy_price)
                                trade_id = uuid.uuid4()
                                buy_df = {'symbol': share, 'trade_type': 'buy', 'quantity': quantity,
                                          'price': buy_price,
                                          'order_execution_time': order_execution_time
                                    , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name,
                                          'stop_loss': stoploss,'instrument_type':'equity','broker':'angle'}
                                self.df = self.df.append(buy_df, ignore_index=True)
                                in_trade = True
                                watch = False
                                index = break_out_idx + 1
                                break
                            else:
                                for i in range((cnadle_in_trade_interval * self.narrow_range) - 1):
                                    index = index + 1
                                    if trade_data['low'][index] < self.high_range < trade_data['close'][index] and \
                                            trade_data['open'][index] < trade_data['close'][index]:
                                        buy_price = trade_data['close'][index]
                                        stoploss_diff = buy_price - stoploss
                                        target = buy_price + (self.high_range - self.low_range)
                                        order_execution_time = trade_data['datetime'][index]
                                        quantity = math.ceil(self.amount_per_share / buy_price)
                                        trade_id = uuid.uuid4()
                                        buy_df = {'symbol': share, 'trade_type': 'buy', 'quantity': quantity,
                                                  'price': buy_price,
                                                  'order_execution_time': order_execution_time
                                            , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name,
                                                  'stop_loss': stoploss,'instrument_type':'equity','broker':'angle'}
                                        self.df = self.df.append(buy_df, ignore_index=True)
                                        in_trade = True
                                        watch = False
                                        break
                            watch = False
                            break
                        index = index + 1
                    range_date = self.get_str_date(trade_data['datetime'][index], self.time_interval[0])
                    range_index = self.range_data.index[self.range_data['datetime'] == range_date].tolist()[0]

                else:
                    if in_trade:
                        if self.range_data['high'][ind] >= target and not half_booked:
                            half_booked = True
                            booked_quant = math.ceil(quantity/2)
                            sell_df = {'symbol': share, 'trade_type': 'sell', 'quantity': booked_quant,
                                       'price': target,
                                       'order_execution_time': self.range_data['datetime'][ind]
                                , 'system_trade_id': trade_id, 'interval': self.time_interval[0].name,
                                       'stop_loss': stoploss,'instrument_type':'equity','broker':'angel'}
                            quantity = quantity - booked_quant
                            self.df = self.df.append(sell_df, ignore_index=True)
                        else:
                            if self.range_data['low'][ind] <= stoploss:
                                in_trade = False
                                half_booked = False
                                sell_df = {'symbol': share, 'trade_type': 'sell', 'quantity': quantity,
                                           'price': stoploss,
                                           'order_execution_time': self.range_data['datetime'][ind]
                                    , 'system_trade_id': trade_id, 'interval': self.time_interval[0].name,
                                           'stop_loss': stoploss,'instrument_type':'equity','broker':'angel'}
                                self.df = self.df.append(sell_df, ignore_index=True)
                        if half_booked:
                            stoploss_new = self.range_data['close'][ind] - stoploss_diff
                            if stoploss_new > stoploss:
                                stoploss = stoploss_new

        Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
                                   self.__class__.__name__ + '_' + str(self.narrow_range) + '_'+'trail')

    # with trailing stoploss at start
    # def backtest_strategy(self):
    #     self.df = Util.get_trade_sheet_df()
    #     for share in self.share_name:
    #         print(share)
    #         self.range_data = self.data_list.get(share + '_' + self.time_interval[0].name)
    #         trade_data = self.data_list.get(share + '_' + self.time_interval[1].name)
    #         trade_data.index = np.arange(0, len(trade_data))
    #         first_date = trade_data['datetime'][0]
    #         convert_date = self.get_str_date(first_date, self.time_interval[0])
    #         index = self.range_data.index[self.range_data['datetime'] == convert_date].tolist()[0]
    #         self.range_data = self.range_data[index - self.range_data.index[0]:self.range_data.index[-1]]
    #         self.range_data.index = np.arange(0, len(self.range_data))
    #         watch = False
    #         in_trade = False
    #         half_booked = False
    #         cnadle_in_trade_interval = Util.get_candles_per_day(self.time_interval[1])
    #         range_index = 3
    #         stoploss = 0
    #         stoploss_diff = 0
    #         target = 0
    #         trade_id = ''
    #         for ind in self.range_data.index:
    #             if not ind > range_index:
    #                 continue
    #             if not watch and not in_trade:
    #                 watch = self.is_narrow_range(ind)
    #                 continue
    #
    #             if watch:
    #                 trade_date = self.get_str_date(self.range_data['datetime'][ind], self.time_interval[1])
    #                 try:
    #                     index = trade_data.index[trade_data['datetime'] == trade_date].tolist()[0]
    #                 except:
    #                     watch = False
    #                     continue
    #                 in_loop = True
    #                 while in_loop:
    #                     if not index + (cnadle_in_trade_interval * self.narrow_range) - 1 in trade_data.index:
    #                         index = trade_data.index[-1]
    #                         watch = False
    #                         break
    #                     if self.high_range < trade_data['close'][index]:
    #                         break_out_idx = index
    #                         break_out_date = self.get_str_date(trade_data['datetime'][break_out_idx],
    #                                                            self.time_interval[0])
    #                         breakout_range_index = \
    #                             self.range_data.index[self.range_data['datetime'] == break_out_date].tolist()[0]
    #                         if self.range_data['low'][breakout_range_index] < self.range_data['low'][
    #                             breakout_range_index - 1]:
    #                             stoploss = self.range_data['low'][breakout_range_index]
    #                         else:
    #                             stoploss = self.range_data['low'][breakout_range_index - 1]
    #                         if trade_data['close'][break_out_idx] < trade_data['close'][break_out_idx + 1]:
    #                             buy_price = trade_data['close'][break_out_idx + 1]
    #                             stoploss_diff = buy_price - stoploss
    #                             target = buy_price + (self.high_range - self.low_range)
    #                             order_execution_time = trade_data['datetime'][break_out_idx + 1]
    #                             quantity = math.ceil(self.amount_per_share / buy_price)
    #                             trade_id = uuid.uuid4()
    #                             buy_df = {'symbol': share, 'trade_type': 'buy', 'quantity': quantity,
    #                                       'price': buy_price,
    #                                       'order_execution_time': order_execution_time
    #                                 , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name,
    #                                       'stop_loss': stoploss}
    #                             self.df = self.df.append(buy_df, ignore_index=True)
    #                             in_trade = True
    #                             watch = False
    #                             index = break_out_idx + 1
    #                             break
    #                         else:
    #                             for i in range((cnadle_in_trade_interval * self.narrow_range) - 1):
    #                                 index = index + 1
    #                                 if trade_data['low'][index] < self.high_range < trade_data['close'][index] and \
    #                                         trade_data['open'][index] < trade_data['close'][index]:
    #                                     buy_price = trade_data['close'][index]
    #                                     stoploss_diff = buy_price - stoploss
    #                                     target = buy_price + (self.high_range - self.low_range)
    #                                     order_execution_time = trade_data['datetime'][index]
    #                                     quantity = math.ceil(self.amount_per_share / buy_price)
    #                                     trade_id = uuid.uuid4()
    #                                     buy_df = {'symbol': share, 'trade_type': 'buy', 'quantity': quantity,
    #                                               'price': buy_price,
    #                                               'order_execution_time': order_execution_time
    #                                         , 'system_trade_id': trade_id, 'interval': self.time_interval[1].name,
    #                                               'stop_loss': stoploss}
    #                                     self.df = self.df.append(buy_df, ignore_index=True)
    #                                     in_trade = True
    #                                     watch = False
    #                                     break
    #                         watch = False
    #                         break
    #                     index = index + 1
    #                 range_date = self.get_str_date(trade_data['datetime'][index], self.time_interval[0])
    #                 range_index = self.range_data.index[self.range_data['datetime'] == range_date].tolist()[0]
    #
    #             else:
    #                 if in_trade:
    #                     if self.range_data['low'][ind] <= stoploss:
    #                         in_trade = False
    #                         sell_df = {'symbol': share, 'trade_type': 'sell', 'quantity': quantity,
    #                                    'price': stoploss,
    #                                    'order_execution_time': self.range_data['datetime'][ind]
    #                             , 'system_trade_id': trade_id, 'interval': self.time_interval[0].name,
    #                                    'stop_loss': stoploss}
    #                         self.df = self.df.append(sell_df, ignore_index=True)
    #
    #                     stoploss_new = self.range_data['close'][ind] - stoploss_diff
    #                     if stoploss_new > stoploss:
    #                         stoploss = stoploss_new
    #
    #     Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
    #                                self.__class__.__name__ + '_' + str(self.narrow_range)+'start_trail')

    def buy_share(self):
        pass

    def sell_share(self):
        pass
