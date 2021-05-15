import enum

import pandas as pd
import os
from datetime import datetime

class Util:


    @staticmethod
    def get_symbol_token(name):
        symbol_dataframe = pd.read_csv('symbol.csv')
        symbol = symbol_dataframe[symbol_dataframe['symbol'] == name]
        if symbol.empty:
            return None
        else:
            return symbol['token'].iloc[0]

    @staticmethod
    def get_share_name_token(token):
        symbol_dataframe = pd.read_csv('symbol.csv')
        symbol = symbol_dataframe[symbol_dataframe['token'] == token]
        if symbol.empty:
            return None
        else:
            return symbol['name'].iloc[0]

    @staticmethod
    def get_ist_to_date(datetime):
        return datetime.replace(hour=23, minute=59, second=0, microsecond=0)

    @staticmethod
    def get_ist_from_date(datetime):
        return datetime.replace(hour=00, minute=00, second=0, microsecond=0)

    @staticmethod
    def get_hour_end_date(datetime,interval):
        if interval in [interval_enum.ONE_HOUR, interval_enum.THIRTY_MINUTE, interval_enum.FIFTEEN_MINUTE] :
            return datetime.replace(hour=15, minute=15, second=0, microsecond=0)
        if interval in [interval_enum.FIVE_MINUTE, interval_enum.TEN_MINUTE]:
            return datetime.replace(hour=15, minute=25, second=0, microsecond=0)
        if interval == interval_enum.THREE_MINUTE:
            return datetime.replace(hour=15, minute=27, second=0, microsecond=0)
        if interval == interval_enum.ONE_MINUTE:
            return datetime.replace(hour=15, minute=29, second=0, microsecond=0)

        return datetime.replace(hour=0, minute=0, second=0, microsecond=0)


    @staticmethod
    def get_hour_start_date(datetime,interval):
        if interval not in [interval_enum.ONE_DAY, interval_enum.ONE_WEEK, interval_enum.ONE_MONTH] :
              return datetime.replace(hour=9, minute=15, second=0, microsecond=0)
        else:
            return datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        return datetime

    @staticmethod
    def convert_dataframe_csv(dataframe, path, name):
        if not os.path.exists(path):
            os.makedirs(path)
        if '.csv' in name:
            dataframe.to_csv(path + '/' + name)
        else:
            dataframe.to_csv(path + '/' + name + '.csv')

    @staticmethod
    def read_csv_df(path):
        if '.csv' in path:
            df = pd.read_csv(path)
        else:
            df = pd.read_csv(path + '.csv')
        df.drop(df.columns[df.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
        return df


    @staticmethod
    def get_angle_data_df():
        return pd.DataFrame(columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])

    @staticmethod
    def convert_str_date(str_date):
        if 'T' in str_date:
            return datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.strptime(str_date.split(" ")[0], "%Y-%m-%d")

    @staticmethod
    def get_candles_per_day(interval):
        if interval == interval_enum.ONE_MINUTE:
            return 375
        if interval == interval_enum.ONE_HOUR:
            return 7
        if interval == interval_enum.FIVE_MINUTE:
            return 75
        if interval == interval_enum.FIFTEEN_MINUTE:
            return 25
        if interval == interval_enum.THIRTY_MINUTE:
            return 13
        if interval == interval_enum.TEN_MINUTE:
            return 38
        if interval == interval_enum.THREE_MINUTE:
            return 125
        if interval == interval_enum.ONE_DAY:
            return 1

    @staticmethod
    def get_trade_sheet_df():
        df = pd.DataFrame(
            columns=['symbol', 'trade_type', 'quantity', 'price', 'order_execution_time', 'system_trade_id',
                     'interval', 'stop_loss'])
        return df

class trend_type(enum.Enum):
    STRONG_DOWN = 0
    DOWN = 1
    Neutral = 2
    UP = 3
    STRONG_UP = 4


class interval_enum(enum.Enum):
    ONE_MINUTE = 1
    THREE_MINUTE = 3
    FIVE_MINUTE = 5
    TEN_MINUTE = 10
    FIFTEEN_MINUTE = 15
    THIRTY_MINUTE = 30
    ONE_HOUR = 60
    ONE_DAY = 375
    ONE_WEEK = 1875
    ONE_MONTH = 7500