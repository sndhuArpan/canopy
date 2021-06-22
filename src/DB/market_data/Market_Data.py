import math
import sqlite3
import os
from datetime import datetime, timedelta
import time
import pandas as pd

import numpy as np

from src.DB.market_data.exchange_mapping import exchange_mapping
from src.DB.static_db.BrokerAppDetails import BrokerAppDetails
from utils.Utils import Utils


class LtpPriceModel:
    def __init__(self):
        self.token = None
        self.ltp_price = None
        self.ltp_time = ''
        self.volume = None
        self.exchange = ''

    def initialize(self, token, exchange):
        self.token = token
        self.exchange = exchange
        return self


class TickerMsg:
    def __init__(self):
        self.time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.message = None
        self.status = None

    def initialize(self, message, status):
        self.status = status
        self.message = message
        return self


class MarketData:

    def __init__(self):
        get_file_dir = os.path.dirname(__file__)
        db_file = os.path.join(get_file_dir, '../../../db_files/market_data.db')
        self.conn = sqlite3.connect(db_file, check_same_thread=False)

    def create_ticker_message_table(self):
        create_table = 'Create table ticker_message ' + '''(time varchar2(20),
                         message       varchar2(20) NOT NULL PRIMARY KEY,
                         status        varchar2(10));'''
        self.conn.execute(create_table)
        self.conn.commit()

    def create_market_data_table(self):
        create_table = 'Create table market_data ' + '''(token int NOT NULL PRIMARY KEY,
                 ltp_price       int,
                 ltp_time   varchar(10),
                 volume   int ,
                 exchange        varchar(10) NOT NULL);'''
        self.conn.execute(create_table)
        self.conn.commit()

    def __insert_table_daily_query(self):
        insert_query = 'INSERT INTO market_data (token, exchange) values({token}, "{exchange}")'
        return insert_query

    def register_token(self, model):
        # check token already register
        check_query = '''select count(*) from market_data where token = "{token}" and exchange = "{exchange}"'''
        cursor = self.conn.execute(check_query.format(token=model.token, exchange=model.exchange))
        for row in cursor:
            if row[0] >= 1:
                pass
            else:
                query = self.__insert_table_daily_query().format(token=model.token, exchange=model.exchange)
                self.conn.execute(query)
                self.conn.commit()

    def deregister_token(self, token):
        query = 'delete from market_data where token = {token}'.format(token=token)
        self.conn.execute(query)
        self.conn.commit()

    def auto_deregister_token(self):
        get_all_token_and_llp = '''select token, ltp_time from market_data'''
        cursor = self.conn.execute(get_all_token_and_llp)
        for row in cursor:
            token = row[0]
            ltp_time = row[1]
            if ltp_time is None:
                self.deregister_token(token)
            else:
                last_trade_time = datetime.datetime.strptime(ltp_time, '%d/%m/%Y %H:%M:%S')
                if last_trade_time < (datetime.datetime.now() - datetime.timedelta(seconds=120)):
                    self.deregister_token(token)

    def deregister_all_token(self):
        query = 'delete from market_data'
        self.conn.execute(query)
        self.conn.commit()

    def update_ltp(self, model):
        update_query = 'Update market_data set'
        if model.ltp_price is not None or model.ltp_time is not None or model.volume is not None:
            if model.ltp_price:
                update_query = update_query + ' ltp_price={ltp_price},'
            if model.ltp_time:
                update_query = update_query + ' ltp_time="' + model.ltp_time + '",'
            if model.volume:
                update_query = update_query + ' volume={volume},'
            update_query = update_query[0:update_query.__len__() - 1] + ' where  token = {token}'
            if model.ltp_price and model.volume:
                update_query = update_query.format(ltp_price=model.ltp_price,
                                                   volume=model.volume,
                                                   token=model.token)
            else:
                if model.volume:
                    update_query = update_query.format(volume=model.volume,
                                                       token=model.token)
                if model.ltp_price:
                    update_query = update_query.format(ltp_price=model.ltp_price,
                                                       token=model.token)
                else:
                    update_query = update_query.format(token=model.token)
        else:
            update_query = update_query + ' ltp_price = null, ltp_time = null, volume = null where token = {token} '
            update_query = update_query.format(token=model.token)

        self.conn.execute(update_query)
        self.conn.commit()

    def __select_columns(self):
        return ' token,ltp_price,ltp_time,volume,exchange '

    def __convert_row_model(self, cursor):
        model = LtpPriceModel()
        for row in cursor:
            model.token = row[0]
            model.ltp_price = row[1]
            model.ltp_time = row[2]
            model.volume = row[3]
            model.exchange = row[4]
        return model

    def get_market_data(self, token):
        select_query = 'select ' + self.__select_columns() + ' from market_data where token ={token}'
        cursor = self.conn.execute(select_query.format(token=token))
        return self.__convert_row_model(cursor)

    def get_register_token_string(self):
        select_query = 'select token,exchange from market_data '
        cursor = self.conn.execute(select_query)
        websocket_ticker = ''
        for row in cursor:
            token = str(row[0])
            exchange = row[1]
            websocket_exchange = exchange_mapping.__getitem__(exchange).value
            websocket_ticker = websocket_ticker + websocket_exchange + '|' + token + '&'

        return websocket_ticker[0:websocket_ticker.__len__() - 1]

    def get_all_register_token(self):
        select_query = 'select token,exchange from market_data '
        cursor = self.conn.execute(select_query)
        token_list = []
        for row in cursor:
            if row:
                token_list.append([row[0], row[1]])
        return token_list

    def _check_ticker_message(self, message):
        select_query = 'select count(*) from ticker_message where message = "{message}"'
        cursor = self.conn.execute(select_query.format(message=message))
        for row in cursor:
            if row[0] == 0:
                return False
            else:
                return True

    def insert_into_ticker_message(self, model):
        if self._check_ticker_message(model.message):
            update_query = 'Update ticker_message set time = "{time}" and status = "{status}" where message = "{message}"'
            update_query = update_query.format(time=model.time,
                                               status=model.status,
                                               message=model.message)
            self.conn.execute(update_query)
            self.conn.commit()
        else:
            insert_query = 'INSERT INTO ticker_message (time, message, status) values("{time}", "{message}", "{status}")'
            query = insert_query.format(time=model.time, message=model.message, status=model.status)
            self.conn.execute(query)
            self.conn.commit()

    def get_max_last_traded_time(self):
        select_query = 'select max(ltp_time) from market_data'
        cursor = self.conn.execute(select_query)
        for row in cursor:
            if row:
                return row[0]
            else:
                return None

    def get_ltp_data(self, exchange, symbol, token):
        connection = BrokerAppDetails().get_normal_connection('S705342')
        data = connection.ltpData(exchange, symbol, token).__getitem__('data')
        return data

    def get_candle_data(self, **kwargs):
        share_symbol = str(kwargs.get('share_symbol'))
        number_of_candles = kwargs.get('candles')
        interval = kwargs.get('interval')
        exchange = kwargs.get('exchange')
        if number_of_candles:
            from_date = Utils.get_ist_from_date(datetime.today() - timedelta(days=number_of_candles)).strftime(
                "%Y-%m-%d %H:%M")
        else:
            from_date = Utils.get_ist_from_date(datetime.today()).strftime("%Y-%m-%d %H:%M")
        to_date = Utils.get_ist_to_date(datetime.today()).strftime("%Y-%m-%d %H:%M")

        historicParam = {
            "exchange": exchange,
            "symboltoken": share_symbol,
            "interval": interval.name,
            "fromdate": from_date,
            "todate": to_date
        }
        while True:
            try:
                data = BrokerAppDetails().get_normal_connection('S705342').getCandleData(historicParam).__getitem__("data")
                break
            except:
                time.sleep(1)
        if data:
            data_df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            return data_df
        else:
            return pd.DataFrame()


if __name__ == '__main__':
    database_conn = MarketData()
    database_conn.auto_deregister_token()
    # print(database_conn.get_max_last_traded_time())
    # import time
    # model1 = LtpPriceModel().initialize(220822, 'MCX')
    # model2 = LtpPriceModel().initialize(220822, 'MCX')
    # model3 = LtpPriceModel().initialize(228925, 'MCX')
    # model4 = LtpPriceModel().initialize(221598, 'MCX')
    # # model5 = LtpPriceModel().initialize(11364, 'NSE')
    # database_conn = MarketData()
    # database_conn.register_token(model1)
    # database_conn = MarketData()
    # database_conn.register_token(model2)
    # database_conn = MarketData()
    # database_conn.register_token(model3)
    # database_conn = MarketData()
    # database_conn.register_token(model4)
    # while True:
    #     database_conn = MarketData()
    #     database_conn.register_token(model5)
    #     time.sleep(10)
    #     database_conn = MarketData()
    #     database_conn.deregister_token(11364)
    #     time.sleep(10)
