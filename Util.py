import enum

import pandas as pd
import os


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
    def convert_dataframe_csv(dataframe, path, name):
        if not os.path.exists(path):
            os.makedirs(path)
        if '.csv' in name:
            dataframe.to_csv(path + '/' + name)
        else:
            dataframe.to_csv(path + '/' + name + '.csv')


class interval_enum(enum.Enum):
    ONE_MINUTE = 1
    THREE_MINUTE = 3
    FIVE_MINUTE = 5
    TEN_MINUTE = 10
    FIFTEEN_MINUTE = 15
    THIRTY_MINUTE = 30
    ONE_HOUR = 60
    ONE_DAY = 1440
    ONE_WEEK = 7
    ONE_MONTH = 30