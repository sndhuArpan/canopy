import uuid
from datetime import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
from Data_Wrappers.Strategy.strategy_wrapper import strategy_wrapper
from Util import interval_enum, Util
import math


class narrow(strategy_wrapper):
    def __init__(self):
        self.amount = 100000
        self.narrow_range = 7
        self.share_name = ['ADANIPORTS-EQ', 'ASIANPAINT-EQ', 'AXISBANK-EQ', 'BAJFINANCE-EQ', 'BAJAJFINSV-EQ',
                           'BPCL-EQ', 'BHARTIARTL-EQ', 'CIPLA-EQ', 'COALINDIA-EQ',
                           'DRREDDY-EQ', 'EICHERMOT-EQ', 'GAIL-EQ', 'GRASIM-EQ', 'HCLTECH-EQ',
                           'HDFCBANK-EQ', 'HEROMOTOCO-EQ', 'HINDALCO-EQ', 'HINDPETRO-EQ', 'HINDUNILVR-EQ',
                           'HDFC-EQ', 'ITC-EQ', 'ICICIBANK-EQ', 'IOC-EQ', 'INDUSINDBK-EQ',
                           'INFY-EQ', 'JSWSTEEL-EQ', 'KOTAKBANK-EQ', 'LT-EQ', 'MARUTI-EQ',
                           'NTPC-EQ', 'ONGC-EQ', 'POWERGRID-EQ', 'RELIANCE-EQ',
                           'SUNPHARMA-EQ', 'TCS-EQ', 'TATAMOTORS-EQ', 'TATASTEEL-EQ', 'TECHM-EQ',
                           'TITAN-EQ', 'UPL-EQ', 'ULTRACEMCO-EQ', 'VEDL-EQ', 'WIPRO-EQ',
                           'YESBANK-EQ', 'ZEEL-EQ']
        # self.share_name = ['TCS-EQ']

        self.amount_per_share = 20000
        self.stop_loss_bars = 1
        self.time_interval = [interval_enum.ONE_DAY, interval_enum.ONE_HOUR]
        broker = 'angle'
        self.start_date = datetime.today() - relativedelta(years=9)
        self.end_date = datetime.today()
        super().__init__(share_name=self.share_name, time_interval=self.time_interval, broker=broker,
                         start_date=self.start_date, end_date=datetime.today())

    def is_narrow_range(self, ind):
        if not ind - self.narrow_range in self.range_data['high'].index:
            return False
        range_check = self.range_data['high'][ind] - self.range_data['low'][ind]
        for i in range(self.narrow_range - 1):
            current_candle_idx = ind - 1 - i
            current_candle_range = self.range_data['high'][current_candle_idx] - self.range_data['low'][
                current_candle_idx]
            if current_candle_range >= range_check:
                continue
            else:
                return False
        if self.range_data['high'][ind] < self.range_data['low'][ind - self.narrow_range +1]:
            return True
        else:
            return False

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
            cnadle_in_trade_interval = Util.get_candles_per_day(self.time_interval[1])
            watch = False
            in_buy_Trade = False
            stop_loss = 0
            quantity = 0
            in_sell_Trade = False
            trade_id = ''
            for ind in self.range_data.index:
                if not watch and not in_sell_Trade and not in_buy_Trade:
                    watch = self.is_narrow_range(ind)
                    continue

                if watch:
                    trade_date = self.get_str_date(self.range_data['datetime'][ind], self.time_interval[1])
                    try:
                        index = trade_data.index[trade_data['datetime'] == trade_date].tolist()[0]
                    except:
                        watch = False
                        continue
                    previous_high = self.range_data['high'][ind - 1]
                    previous_low = self.range_data['low'][ind - 1]
                    if trade_data['open'][index] > self.range_data['close'][ind - 1]:
                        for i in range(cnadle_in_trade_interval):
                            if trade_data['close'][index + i] >= previous_high and trade_data['close'][index + i] > trade_data['open'][index + i] and not in_buy_Trade:
                                in_buy_Trade = True
                                buy_price = trade_data['close'][index + i]
                                stop_loss = previous_low
                                trade_id = uuid.uuid4()
                                quantity = math.ceil(self.amount_per_share/buy_price)
                                buy_df = dict(symbol=share, trade_type='buy', quantity=quantity, price=buy_price,
                                              order_execution_time=trade_data['datetime'][index + i],
                                              system_trade_id=trade_id,
                                              interval=self.time_interval[1].name, stop_loss=stop_loss,
                                              instrument_type='equity',
                                              broker='angel')
                                self.df = self.df.append(buy_df, ignore_index=True)
                            if in_buy_Trade and trade_data['close'][index + i] < previous_high:
                                in_buy_Trade = False
                                sell_df = dict(symbol=share, trade_type='sell', quantity=quantity, price=trade_data['close'][index + i],
                                              order_execution_time=trade_data['datetime'][index + i],
                                              system_trade_id=trade_id,
                                              interval=self.time_interval[1].name, stop_loss=stop_loss,
                                              instrument_type='equity',
                                              broker='angel')
                                self.df = self.df.append(sell_df, ignore_index=True)
                                break

                    if trade_data['open'][index] < self.range_data['close'][ind - 1]:
                        for i in range(cnadle_in_trade_interval):
                            if trade_data['low'][index + i] <= previous_low:
                                # in_sell_Trade = True
                                sell_price = previous_low
                                stop_loss = previous_high
                                trade_id = uuid.uuid4()
                                quantity = math.ceil(self.amount_per_share / sell_price)
                                sell_df = dict(symbol=share, trade_type='sell', quantity=quantity, price=sell_price,
                                              order_execution_time=trade_data['datetime'][index + i],
                                              system_trade_id=trade_id,
                                              interval=self.time_interval[1].name, stop_loss=stop_loss,
                                              instrument_type='equity',
                                              broker='angel')
                                # self.df = self.df.append(sell_df, ignore_index=True)
                                break
                    watch = False

                if in_buy_Trade:
                    if self.range_data['close'][ind] <= stop_loss:
                        sell_df = dict(symbol=share, trade_type='sell', quantity=quantity, price=self.range_data['close'][ind],
                                       order_execution_time=self.range_data['datetime'][ind],
                                       system_trade_id=trade_id,
                                       interval=self.time_interval[0].name, stop_loss=stop_loss,
                                       instrument_type='equity',
                                       broker='angel')
                        self.df = self.df.append(sell_df, ignore_index=True)
                        in_buy_Trade = False
                    else:
                        stop_loss = self.range_data['low'][ind + 1 - self.stop_loss_bars]

                if in_sell_Trade:
                    if self.range_data['high'][ind] >= stop_loss:
                        buy_df = dict(symbol=share, trade_type='buy', quantity=quantity, price=stop_loss,
                                       order_execution_time=self.range_data['datetime'][ind],
                                       system_trade_id=trade_id,
                                       interval=self.time_interval[0].name, stop_loss=stop_loss,
                                       instrument_type='equity',
                                       broker='angel')
                        self.df = self.df.append(buy_df, ignore_index=True)
                        in_sell_Trade = False
                    else:
                        stop_loss = self.range_data['high'][ind + 1 - self.stop_loss_bars]

        Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
                                   self.__class__.__name__ + '_' + str(self.narrow_range))



    def buy_share(self):
        pass

    def sell_share(self):
        pass

    def get_str_date(self, date, interval):
        convert_date = Util.get_hour_start_date(Util.convert_str_date(date), interval)
        convert_date = convert_date.strftime("%Y-%m-%dT%H:%M:%S")
        return convert_date
