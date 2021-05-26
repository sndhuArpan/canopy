import sqlite3
import os

from src.DB.market_data.exchange_mapping import exchange_mapping


class ltp_price_model:
    def __init__(self):
        self.token = None
        self.ltp_price = None
        self.ltp_time = ''
        self.volume = None
        self.exchange = ''

    def initialze(self, token, exchange):
        self.token = token
        self.exchange = exchange


class market_data:

    def __init__(self):
        get_file_dir = os.path.dirname(__file__)
        db_file = os.path.join(get_file_dir, 'market_data.db')
        self.conn = sqlite3.connect(db_file)

    def create_market_data_table(self):
        create_table = 'Create table market_data ' + '''(token int NOT NULL PRIMARY KEY,
                 ltp_price       int,
                 ltp_time   varchar(10),
                 volume   int ,
                 exchange        varchar(10) NOT NULL);'''
        self.conn.execute(create_table)
        self.conn.commit()
        self.conn.close()

    def __insert_table_daily_query(self):
        insert_query = 'INSERT INTO market_data (token, exchange) values({token}, "{exchange}")'
        return insert_query

    def register_token(self, model):
        query = self.__insert_table_daily_query().format(token=model.token,
                                                         exchange=model.exchange)
        self.conn.execute(query)
        self.conn.commit()
        self.conn.close()

    def deregister_token(self, token):
        query = 'delete from market_data where token = {token}'.format(token=token)
        self.conn.execute(query)
        self.conn.commit()
        self.conn.close()

    def update_ltp(self, model):
        update_query = 'Update market_data set'
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

        self.conn.execute(update_query)
        self.conn.commit()

    def __select_columns(self):
        return ' token,ltp_price,ltp_time,volume,exchange '

    def __convert_row_model(self, cursor):
        model = ltp_price_model()
        for row in cursor:
            model.token = row[0]
            model.ltp_price = row[1]
            model.ltp_time = row[2]
            model.volume = row[3]
            model.exchange = row[4]
        return model

    def select_model_token(self, token):
        select_query = 'select ' + self.__select_columns() + ' from market_data where token ={token}'
        cursor = self.conn.execute(select_query.format(token=token))
        return self.__convert_row_model(cursor)

    def get_all_tokens(self):
        select_query = 'select token,exchange from market_data '
        cursor = self.conn.execute(select_query)
        websocket_ticker = ''
        for row in cursor:
            token = str(row[0])
            exchange = row[1]
            websocket_exchange = exchange_mapping.__getitem__(exchange).value
            websocket_ticker = websocket_ticker + websocket_exchange+'|'+token + '&'

        return websocket_ticker[0:websocket_ticker.__len__() - 1]
