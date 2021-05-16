import enum
from Data_Wrappers.Angel_Broker.Angel_Broker_Wrapper import Angel_Broker_Wrapper
from Data_Wrappers.Indicators.EMA import EMA
from Util import Util, interval_enum, trend_type
import os
import pandas as pd
import math
from datetime import datetime, timedelta


class trend_term(enum.Enum):
    SHORT_TERM = [8, 13]
    MID_TERM = [13, 23]
    LONG_TERM = [23, 53]


class Trend:
    def __init__(self, term, trade_interval):
        self.average_weight = [1, 0.8, 0.5]
        self.term = trend_term.__getitem__(term.name).value
        if trade_interval == interval_enum.FIVE_MINUTE:
            self.interval = [interval_enum.FIVE_MINUTE, interval_enum.THIRTY_MINUTE, interval_enum.ONE_DAY]
        if trade_interval == interval_enum.FIFTEEN_MINUTE:
            self.interval = [interval_enum.FIFTEEN_MINUTE, interval_enum.ONE_HOUR, interval_enum.ONE_DAY]
        if trade_interval == interval_enum.ONE_HOUR:
            self.interval = [interval_enum.ONE_HOUR, interval_enum.ONE_DAY, interval_enum.ONE_WEEK]
        if trade_interval == interval_enum.ONE_DAY:
            self.interval = [interval_enum.ONE_DAY, interval_enum.ONE_WEEK]
        if trade_interval == interval_enum.ONE_WEEK:
            self.interval = [interval_enum.ONE_WEEK, interval_enum.ONE_MONTH]

    def get_trend(self,trend_date,**kwargs):
        if kwargs.get('share'):
            self.share = Util.get_symbol_token(kwargs.get('share'))
        if kwargs.get('share_symbol'):
            self.share = kwargs.get('share_symbol')
        trend_date = Util.convert_str_date(trend_date)
        max_period = {}
        for i in self.interval:
            if i not in [interval_enum.ONE_WEEK, interval_enum.ONE_MONTH]:
                per_day_candle = Util.get_candles_per_day(i)
                max_days_req = math.ceil(((1/per_day_candle)*self.term[1])*2)
            else:
                if i == interval_enum.ONE_WEEK:
                    max_days_req = 14*self.term[1]
                if i == interval_enum.ONE_MONTH:
                    max_days_req = 60*self.term[1]
            max_period[i.name] = max_days_req
        indicators = [EMA(interval=self.term[0], on='close'), EMA(interval=self.term[1], on='close')]

        trend_value = []

        angle_broker = Angel_Broker_Wrapper()
        for time_interval in self.interval:
            start_date = trend_date - timedelta(days=max_period.get(time_interval.name))
            data = angle_broker.get_symbol_data(self.share, time_interval, start_date=start_date, end_date=trend_date)
            for indicator in indicators:
                data = indicator.cal_indicator(data=data)
            final_row_data = data.iloc[-1]
            few_row_back_data = data.iloc[data.shape[0] - int(self.term[0] / 2)]
            if self.is_uptrend(final_row_data, few_row_back_data):
                trend_value.append(1)
            else:
                if self.is_downtrend(final_row_data, few_row_back_data):
                    trend_value.append(-1)
                else:
                    trend_value.append(0)

        total_weight = 0
        weight = 0
        for i in range(len(trend_value)):
            weight = weight + trend_value[i] * self.average_weight[i]
            total_weight = total_weight + self.average_weight[i]
        trend_weighted_average = weight / total_weight

        low = -1
        add_amount = (2)/trend_type.__len__()

        for i in range(trend_type.__len__()):
            if low+(add_amount*i) <= trend_weighted_average <= low+(add_amount*(i+1)):
                return trend_type._value2member_map_.get(i)


    def is_uptrend(self, final_row, few_row_back):
        ema_1 = 'ema_{0}'.format(str(self.term[0]))
        ema_2 = 'ema_{0}'.format(str(self.term[1]))
        uptrend = False
        if final_row[ema_1] >= final_row[ema_2]:
            if final_row['close'] > final_row[ema_1]:
                if few_row_back[ema_1] < final_row[ema_1] and few_row_back[ema_2] < final_row[ema_2]:
                    uptrend = True
        return uptrend

    def is_downtrend(self, final_row, few_row_back):
        ema_1 = 'ema_{0}'.format(str(self.term[0]))
        ema_2 = 'ema_{0}'.format(str(self.term[1]))
        downTrend = False
        if final_row[ema_1] <= final_row[ema_2]:
            if final_row['close'] < final_row[ema_2]:
                if few_row_back[ema_1] > final_row[ema_1] and few_row_back[ema_2] > final_row[ema_2]:
                    downTrend = True
        return downTrend
