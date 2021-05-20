import uuid
from datetime import datetime , timedelta
import numpy as np
from dateutil.relativedelta import relativedelta

from Data_Wrappers.Indicators.EMA import EMA
from Data_Wrappers.Strategy.strategy_wrapper import strategy_wrapper
from utils.Utils import interval_enum, Utils as Util
import math


class IntraRangeBreak(strategy_wrapper):
    def __init__(self):
        self.amount = 100000
        self.hold_trade = 3
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
        self.share_name = ['HEROMOTOCO-EQ']
        self.quantities = 300
        self.time_interval = [interval_enum.FIFTEEN_MINUTE]
        self.indicators = [EMA(interval=23, on='close')]
        broker = 'angle'
        self.start_date = datetime.today() - relativedelta(years=5)
        self.end_date = datetime.today() - timedelta(days = 2)
        super().__init__(share_name=self.share_name, time_interval=self.time_interval, broker=broker,indicators=self.indicators,
                         start_date=self.start_date, end_date=self.end_date)

    def backtest_strategy(self):
        self.df = Util.get_trade_sheet_df()
        ema_name = 'ema' + '_' + str(self.indicators[0].interval)
        trade_id = ''
        quantity = self.quantities
        stoploss = 0
        for share in self.share_name:
            print(share)
            self.range_data = self.data_list.get(share + '_' + self.time_interval[0].name)
            self.range_data.index = np.arange(0, len(self.range_data))
            start_date = Util.get_hour_start_date(Util.convert_str_date(self.range_data['datetime'][0]), interval_enum.ONE_DAY)
            end_date = Util.get_hour_start_date(Util.convert_str_date(self.range_data['datetime'][self.range_data.index[-1]]),
                                                  interval_enum.ONE_DAY)
            in_buy_trade = False
            in_sell_trade = False
            while start_date < end_date:
                day_start = Util.get_hour_start_date(start_date,self.time_interval[0]).strftime("%Y-%m-%dT%H:%M:%S")
                day_end = Util.get_hour_end_date(start_date,self.time_interval[0]).strftime("%Y-%m-%dT%H:%M:%S")
                try:
                     day_start_index = self.range_data.index[self.range_data['datetime'] == day_start].tolist()[0]
                except:
                    start_date = start_date + timedelta(days=1)
                    continue
                day_end_index = self.range_data.index[self.range_data['datetime'] == day_end].tolist()[0]
                high_range = self.range_data['high'][day_start_index]
                low_range = self.range_data['low'][day_start_index]

                out = 0
                valid_count = 0
                idx = 0
                for i in range(3):
                    idx = day_start_index + 1 + i
                    if self.range_data['open'][idx] <= high_range and self.range_data['close'][idx] <= high_range:
                        if self.range_data['open'][idx] >= low_range and self.range_data['close'][idx] >= low_range:
                            valid_count = valid_count + 1
                            if self.range_data['high'][idx] > high_range or self.range_data['low'][idx] < low_range:
                                out = out + 1

                margin_high_range = self.range_data['high'][day_start_index] - (
                            self.range_data['high'][day_start_index] * 0.15) / 100

                margin_low_range = self.range_data['low'][day_start_index] + (
                            self.range_data['low'][day_start_index] * 0.15) / 100

                if valid_count == 3 and out <= 1:
                    while idx < day_end_index - 6:
                        idx = idx + 1
                        if self.range_data['high'][idx] > high_range and self.range_data['close'][idx-1] > \
                                self.range_data[ema_name][idx-1] > self.range_data[ema_name][day_start_index]:
                            in_buy_trade = True
                            buy_price = high_range
                            trade_id = uuid.uuid4()
                            stoploss = margin_high_range
                            buy_df = dict(symbol=share, trade_type='buy', quantity=quantity, price=buy_price,
                                          order_execution_time=self.range_data['datetime'][idx],
                                          system_trade_id=trade_id,
                                          interval=self.time_interval[0].name, stop_loss=stoploss,
                                          instrument_type='equity',
                                          broker='angel')
                            self.df = self.df.append(buy_df, ignore_index=True)
                            break
                        if self.range_data['low'][idx] < low_range and self.range_data['close'][idx-1] < \
                                self.range_data[ema_name][idx-1] < self.range_data[ema_name][day_start_index]:
                            in_sell_trade = True
                            sell_price = low_range
                            trade_id = uuid.uuid4()
                            stoploss = margin_low_range
                            sell_df = dict(symbol=share, trade_type='sell', quantity=quantity, price=sell_price,
                                          order_execution_time=self.range_data['datetime'][idx],
                                          system_trade_id=trade_id,
                                          interval=self.time_interval[0].name, stop_loss=stoploss,
                                          instrument_type='equity',
                                          broker='angel')
                            self.df = self.df.append(sell_df, ignore_index=True)
                            break

                if in_buy_trade:
                    if self.range_data['close'][idx] < stoploss:
                        in_buy_trade = False
                        sell_price = self.range_data['close'][idx]
                        sell_df = dict(symbol=share, trade_type='sell', quantity=quantity,
                                       price=sell_price,
                                       order_execution_time=self.range_data['datetime'][idx],
                                       system_trade_id=trade_id,
                                       interval=self.time_interval[0].name, stop_loss=stoploss,
                                       instrument_type='equity',
                                       broker='angel')
                        self.df = self.df.append(sell_df, ignore_index=True)
                    else:
                        if idx + self.hold_trade - 1 <= day_end_index:
                            hold_idx = 0
                            for hold in range(self.hold_trade - 1):
                                hold_idx = idx + 1 + hold
                                if self.range_data['low'][hold_idx] < stoploss:
                                    in_buy_trade = False
                                    if self.range_data['open'][hold_idx] < stoploss:
                                        sell_price = self.range_data['open'][hold_idx]
                                    else:
                                        sell_price = stoploss
                                    sell_df = dict(symbol=share, trade_type='sell', quantity=quantity,
                                                   price=sell_price,
                                                   order_execution_time=self.range_data['datetime'][hold_idx],
                                                   system_trade_id=trade_id,
                                                   interval=self.time_interval[0].name, stop_loss=stoploss,
                                                   instrument_type='equity',
                                                   broker='angel')
                                    self.df = self.df.append(sell_df, ignore_index=True)
                                    break
                            if in_buy_trade:
                                in_buy_trade = False
                                sell_price = self.range_data['close'][hold_idx]
                                sell_df = dict(symbol=share, trade_type='sell', quantity=quantity,
                                               price=sell_price,
                                               order_execution_time=self.range_data['datetime'][hold_idx],
                                               system_trade_id=trade_id,
                                               interval=self.time_interval[0].name, stop_loss=stoploss,
                                               instrument_type='equity',
                                               broker='angel')
                                self.df = self.df.append(sell_df, ignore_index=True)
                        else:
                            in_buy_trade = False
                            sell_price = self.range_data['open'][day_end_index]
                            sell_df = dict(symbol=share, trade_type='sell', quantity=quantity,
                                           price=sell_price,
                                           order_execution_time=self.range_data['datetime'][idx],
                                           system_trade_id=trade_id,
                                           interval=self.time_interval[0].name, stop_loss=0,
                                           instrument_type='equity',
                                           broker='angel')
                            self.df = self.df.append(sell_df, ignore_index=True)

                if in_sell_trade:
                    if self.range_data['close'][idx] > stoploss:
                        in_sell_trade = False
                        buy_price = self.range_data['close'][idx]
                        buy_df = dict(symbol=share, trade_type='buy', quantity=quantity,
                                       price=buy_price,
                                       order_execution_time=self.range_data['datetime'][idx],
                                       system_trade_id=trade_id,
                                       interval=self.time_interval[0].name, stop_loss=stoploss,
                                       instrument_type='equity',
                                       broker='angel')
                        self.df = self.df.append(buy_df, ignore_index=True)
                    else:
                        if idx + self.hold_trade - 1 <= day_end_index:
                            hold_idx = 0
                            for hold in range(self.hold_trade - 1):
                                hold_idx = idx + 1 + hold
                                if self.range_data['high'][hold_idx] > stoploss:
                                    in_sell_trade = False
                                    if self.range_data['open'][hold_idx] > stoploss:
                                        buy_price = self.range_data['open'][hold_idx]
                                    else:
                                        buy_price = stoploss
                                    buy_df = dict(symbol=share, trade_type='buy', quantity=quantity,
                                                   price=buy_price,
                                                   order_execution_time=self.range_data['datetime'][hold_idx],
                                                   system_trade_id=trade_id,
                                                   interval=self.time_interval[0].name, stop_loss=stoploss,
                                                   instrument_type='equity',
                                                   broker='angel')
                                    self.df = self.df.append(buy_df, ignore_index=True)
                                    break
                            if in_sell_trade:
                                in_sell_trade = False
                                buy_price = self.range_data['close'][hold_idx]
                                buy_df = dict(symbol=share, trade_type='buy', quantity=quantity,
                                               price=buy_price,
                                               order_execution_time=self.range_data['datetime'][hold_idx],
                                               system_trade_id=trade_id,
                                               interval=self.time_interval[0].name, stop_loss=stoploss,
                                               instrument_type='equity',
                                               broker='angel')
                                self.df = self.df.append(buy_df, ignore_index=True)
                        else:
                            in_sell_trade = False
                            buy_price = self.range_data['open'][day_end_index]
                            buy_df = dict(symbol=share, trade_type='buy', quantity=quantity,
                                           price=buy_price,
                                           order_execution_time=self.range_data['datetime'][idx],
                                           system_trade_id=trade_id,
                                           interval=self.time_interval[0].name, stop_loss=0,
                                           instrument_type='equity',
                                           broker='angel')
                            self.df = self.df.append(buy_df, ignore_index=True)



                start_date = start_date + timedelta(days=1)
        Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
                                   self.__class__.__name__ )

    def backtest_strategy_1(self):
        self.df = Util.get_trade_sheet_df()
        ema_name = 'ema' + '_' + str(self.indicators[0].interval)
        cnadle_in_trade_interval = Util.get_candles_per_day(self.time_interval[0])
        trade_id = ''
        quantity = self.quantities
        stoploss = 0
        for share in self.share_name:
            print(share)
            self.range_data = self.data_list.get(share + '_' + self.time_interval[0].name)
            self.range_data.index = np.arange(0, len(self.range_data))
            start_date = Util.get_hour_start_date(Util.convert_str_date(self.range_data['datetime'][0]), interval_enum.ONE_DAY)
            end_date = Util.get_hour_start_date(Util.convert_str_date(self.range_data['datetime'][self.range_data.index[-1]]),
                                                  interval_enum.ONE_DAY)
            in_buy_trade = False
            in_sell_trade = False
            while start_date < end_date:
                day_start = Util.get_hour_start_date(start_date,self.time_interval[0]).strftime("%Y-%m-%dT%H:%M:%S")
                day_end = Util.get_hour_end_date(start_date,self.time_interval[0]).strftime("%Y-%m-%dT%H:%M:%S")
                try:
                     day_start_index = self.range_data.index[self.range_data['datetime'] == day_start].tolist()[0]
                except:
                    start_date = start_date + timedelta(days=1)
                    continue
                day_end_index = self.range_data.index[self.range_data['datetime'] == day_end].tolist()[0]
                high_range = self.range_data['high'][day_start_index]
                margin_high_range = self.range_data['high'][day_start_index] - (self.range_data['high'][day_start_index]*0.15)/100
                low_range = self.range_data['low'][day_start_index]
                margin_low_range = self.range_data['low'][day_start_index] + (
                            self.range_data['low'][day_start_index] * 0.15) / 100

                out = 0
                valid_count = 0
                idx = 0
                for i in range(3):
                    idx = day_start_index + 1 + i
                    if self.range_data['open'][idx] <= high_range and self.range_data['close'][idx] <= high_range:
                        if self.range_data['open'][idx] >= low_range and self.range_data['close'][idx] >= low_range:
                            valid_count = valid_count + 1
                            if self.range_data['high'][idx] > high_range or self.range_data['low'][idx] < low_range:
                                out = out + 1

                if valid_count == 3 and out <= 1:
                    while idx < day_end_index - 6:
                        idx = idx + 1
                        if self.range_data['close'][idx] > high_range and self.range_data['close'][idx] > \
                                self.range_data[ema_name][idx] > self.range_data[ema_name][day_start_index]:
                            in_buy_trade = True
                            buy_price = self.range_data['close'][idx]
                            trade_id = uuid.uuid4()
                            if margin_high_range > self.range_data['low'][idx]:
                                stoploss = margin_high_range
                            else:
                                stoploss = self.range_data['low'][idx]
                            buy_df = dict(symbol=share, trade_type='buy', quantity=quantity, price=buy_price,
                                          order_execution_time=self.range_data['datetime'][idx],
                                          system_trade_id=trade_id,
                                          interval=self.time_interval[0].name, stop_loss=stoploss,
                                          instrument_type='equity',
                                          broker='angel')
                            self.df = self.df.append(buy_df, ignore_index=True)
                            break
                        if self.range_data['close'][idx] < low_range and self.range_data['close'][idx] < \
                                self.range_data[ema_name][idx] < self.range_data[ema_name][day_start_index]:
                            in_sell_trade = True
                            sell_price = self.range_data['close'][idx]
                            trade_id = uuid.uuid4()
                            if margin_low_range < self.range_data['high'][idx]:
                                stoploss = margin_low_range
                            else:
                                stoploss = self.range_data['high'][idx]
                            sell_df = dict(symbol=share, trade_type='sell', quantity=quantity, price=sell_price,
                                          order_execution_time=self.range_data['datetime'][idx],
                                          system_trade_id=trade_id,
                                          interval=self.time_interval[0].name, stop_loss=stoploss,
                                          instrument_type='equity',
                                          broker='angel')
                            self.df = self.df.append(sell_df, ignore_index=True)
                            break

                if in_buy_trade:
                    for hold in range(self.hold_trade - 1):
                        hold_idx = idx + 1 + hold
                        if self.range_data['low'][hold_idx] < stoploss:
                            in_buy_trade = False
                            sell_df = dict(symbol=share, trade_type='sell', quantity=quantity,
                                           price=stoploss,
                                           order_execution_time=self.range_data['datetime'][hold_idx],
                                           system_trade_id=trade_id,
                                           interval=self.time_interval[0].name, stop_loss=stoploss,
                                           instrument_type='equity',
                                           broker='angel')
                            self.df = self.df.append(sell_df, ignore_index=True)
                            break
                        else:
                            if self.range_data['open'][hold_idx] <= self.range_data['close'][hold_idx]:
                                stoploss = self.range_data['open'][hold_idx]
                            else:
                                stoploss = self.range_data['low'][hold_idx]
                    if in_buy_trade:
                        in_buy_trade = False
                        sell_price = self.range_data['close'][hold_idx]
                        sell_df = dict(symbol=share, trade_type='sell', quantity=quantity,
                                       price=sell_price,
                                       order_execution_time=self.range_data['datetime'][hold_idx],
                                       system_trade_id=trade_id,
                                       interval=self.time_interval[0].name, stop_loss=stoploss,
                                       instrument_type='equity',
                                       broker='angel')
                        self.df = self.df.append(sell_df, ignore_index=True)

                if in_sell_trade:
                    for hold in range(self.hold_trade - 1):
                        hold_idx = idx + 1 + hold
                        if self.range_data['high'][hold_idx] > stoploss:
                            in_sell_trade = False
                            buy_df = dict(symbol=share, trade_type='buy', quantity=quantity,
                                           price=stoploss,
                                           order_execution_time=self.range_data['datetime'][hold_idx],
                                           system_trade_id=trade_id,
                                           interval=self.time_interval[0].name, stop_loss=stoploss,
                                           instrument_type='equity',
                                           broker='angel')
                            self.df = self.df.append(buy_df, ignore_index=True)
                            break
                        else:
                            if self.range_data['open'][hold_idx] >= self.range_data['close'][hold_idx]:
                                stoploss = self.range_data['open'][hold_idx]
                            else:
                                stoploss = self.range_data['high'][hold_idx]
                    if in_sell_trade:
                        in_sell_trade = False
                        buy_price = self.range_data['close'][hold_idx]
                        buy_df = dict(symbol=share, trade_type='buy', quantity=quantity,
                                       price=buy_price,
                                       order_execution_time=self.range_data['datetime'][hold_idx],
                                       system_trade_id=trade_id,
                                       interval=self.time_interval[0].name, stop_loss=stoploss,
                                       instrument_type='equity',
                                       broker='angel')
                        self.df = self.df.append(buy_df, ignore_index=True)


                start_date = start_date + timedelta(days=1)
        Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
                                   self.__class__.__name__ )


    def buy_share(self):
        pass

    def sell_share(self):
        pass

    def get_str_date(self, date, interval):
        convert_date = Util.get_hour_start_date(Util.convert_str_date(date), interval)
        convert_date = convert_date.strftime("%Y-%m-%dT%H:%M:%S")
        return convert_date