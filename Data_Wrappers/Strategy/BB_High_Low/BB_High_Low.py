import uuid
from datetime import datetime , timedelta
import numpy as np
from dateutil.relativedelta import relativedelta

from Data_Wrappers.Indicators.BB import BB
from Data_Wrappers.Strategy.strategy_wrapper import strategy_wrapper
from utils.Utils import interval_enum, Utils as Util
import math


class BB_High_Low(strategy_wrapper):
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
        self.share_name = ['RELIANCE-EQ']
        self.quantities = 100
        self.time_interval = [interval_enum.THIRTY_MINUTE]
        self.indicators = [BB(interval=20, on='close')]
        broker = 'angle'
        self.start_date = datetime.today() - relativedelta(years=1)
        self.end_date = datetime.today() - timedelta(days = 2)
        super().__init__(share_name=self.share_name, time_interval=self.time_interval, broker=broker,indicators=self.indicators,
                         start_date=self.start_date, end_date=self.end_date)


    def backtest_strategy(self):
        self.df = Util.get_trade_sheet_df()
        for share in self.share_name:
            print(share)
            self.range_data = self.data_list.get(share + '_' + self.time_interval[0].name)
            self.range_data.index = np.arange(0, len(self.range_data))
            start_date = Util.get_hour_start_date(Util.convert_str_date(self.range_data['datetime'][0]), interval_enum.ONE_DAY)
            end_date = Util.get_hour_start_date(Util.convert_str_date(self.range_data['datetime'][self.range_data.index[-1]]),
                                                  interval_enum.ONE_DAY)
            in_buy_trade = False
            in_sell_trade = False
            trade_id = ''
            quantity = self.quantities
            stop_loss = 0
            target_1 = 0
            traget_2 = 0
            while start_date < end_date:
                day_start = Util.get_hour_start_date(start_date,self.time_interval[0]).strftime("%Y-%m-%dT%H:%M:%S")
                day_end = Util.get_hour_end_date(start_date,self.time_interval[0]).strftime("%Y-%m-%dT%H:%M:%S")
                try:
                     day_start_index = self.range_data.index[self.range_data['datetime'] == day_start].tolist()[0]
                except:
                    start_date = start_date + timedelta(days=1)
                    continue
                day_end_index = self.range_data.index[self.range_data['datetime'] == day_end].tolist()[0]
                idx = day_start_index
                upper_band = False
                lower_band = False
                high_range = 0
                margin_high_range = 0
                low_range = 0
                margin_low_range = 0
                for i in range(3):
                    idx = idx + i
                    if self.range_data['low'][idx] > self.range_data['upper'][idx]:
                        upper_band = True
                        high_range = self.range_data['high'][idx]
                        low_range = self.range_data['low'][idx]
                        margin_high_range = high_range - (high_range * 0.05) / 100
                        margin_low_range = low_range + (low_range * 0.05) / 100
                        target_1 = self.range_data['mid'][idx]
                        target_2 = self.range_data['lower'][idx]
                    else:
                        break

                if not upper_band:
                    for i in range(3):
                        idx = idx + i
                        if self.range_data['high'][idx] < self.range_data['lower'][idx]:
                            lower_band = True
                            high_range = self.range_data['high'][idx]
                            low_range = self.range_data['low'][idx]
                            margin_high_range = high_range - (high_range * 0.05) / 100
                            margin_low_range = low_range + (low_range * 0.05) / 100
                            target_1 = self.range_data['mid'][idx]
                            target_2 = self.range_data['upper'][idx]
                        else:
                            break

                if upper_band:
                    while idx < day_end_index - 5:
                        if self.range_data['low'][idx] < margin_low_range:
                            in_sell_trade = True
                            sell_price = margin_low_range
                            stop_loss = high_range
                            trade_id = uuid.uuid4()
                            sell_df = dict(symbol=share, trade_type='sell', quantity=quantity, price=sell_price,
                                           order_execution_time=self.range_data['datetime'][idx],
                                           system_trade_id=trade_id,
                                           interval=self.time_interval[0].name, stop_loss=stop_loss,
                                           instrument_type='equity',
                                           broker='angel')
                            self.df = self.df.append(sell_df, ignore_index=True)
                            break
                        idx = idx + 1

                if lower_band:
                    while idx < day_end_index - 5:
                        if self.range_data['high'][idx] > margin_high_range:
                            in_buy_trade = True
                            buy_price = margin_high_range
                            stop_loss = low_range
                            trade_id = uuid.uuid4()
                            buy_df = dict(symbol=share, trade_type='buy', quantity=quantity, price=buy_price,
                                          order_execution_time=self.range_data['datetime'][idx],
                                          system_trade_id=trade_id,
                                          interval=self.time_interval[0].name, stop_loss=stop_loss,
                                          instrument_type='equity',
                                          broker='angel')
                            self.df = self.df.append(buy_df, ignore_index=True)
                            break
                        idx = idx + 1

                if in_buy_trade:
                    for hold in range(day_end_index - idx):
                        hold_idx = idx + hold
                        if self.range_data['low'][hold_idx] < stop_loss:
                            in_buy_trade = False
                            sell_price = stop_loss
                            sell_df = dict(symbol=share, trade_type='sell', quantity=quantity,
                                           price=sell_price,
                                           order_execution_time=self.range_data['datetime'][hold_idx],
                                           system_trade_id=trade_id,
                                           interval=self.time_interval[0].name, stop_loss=stop_loss,
                                           instrument_type='equity',
                                           broker='angel')
                            self.df = self.df.append(sell_df, ignore_index=True)
                            break
                    if in_buy_trade:
                        in_buy_trade = False
                        sell_price = self.range_data['open'][day_end_index]
                        sell_df = dict(symbol=share, trade_type='sell', quantity=quantity,
                                       price=sell_price,
                                       order_execution_time=self.range_data['datetime'][day_end_index-1],
                                       system_trade_id=trade_id,
                                       interval=self.time_interval[0].name, stop_loss=stop_loss,
                                       instrument_type='equity',
                                       broker='angel')
                        self.df = self.df.append(sell_df, ignore_index=True)

                if in_sell_trade:
                    for hold in range(day_end_index - idx):
                        hold_idx = idx + hold
                        if self.range_data['high'][hold_idx] > stop_loss:
                            in_sell_trade = False
                            buy_price = stop_loss
                            buy_df = dict(symbol=share, trade_type='buy', quantity=quantity,
                                           price=buy_price,
                                           order_execution_time=self.range_data['datetime'][hold_idx],
                                           system_trade_id=trade_id,
                                           interval=self.time_interval[0].name, stop_loss=stop_loss,
                                           instrument_type='equity',
                                           broker='angel')
                            self.df = self.df.append(buy_df, ignore_index=True)
                            break
                    if in_sell_trade:
                        in_sell_trade = False
                        buy_price = self.range_data['open'][day_end_index]
                        buy_df = dict(symbol=share, trade_type='buy', quantity=quantity,
                                       price=buy_price,
                                       order_execution_time=self.range_data['datetime'][day_end_index-1],
                                       system_trade_id=trade_id,
                                       interval=self.time_interval[0].name, stop_loss=stop_loss,
                                       instrument_type='equity',
                                       broker='angel')
                        self.df = self.df.append(buy_df, ignore_index=True)

                start_date = start_date + timedelta(days=1)
            Util.convert_dataframe_csv(self.df, 'trades/' + self.__class__.__name__,
                                       self.__class__.__name__+'_Loss Only')




    def buy_share(self):
        pass

    def sell_share(self):
        pass

    def get_str_date(self, date, interval):
        convert_date = Util.get_hour_start_date(Util.convert_str_date(date), interval)
        convert_date = convert_date.strftime("%Y-%m-%dT%H:%M:%S")
        return convert_date