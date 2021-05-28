import sqlite3
import os
import requests
import pandas as pd

class TickerInfo:

    def __init__(self, token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size):
        self.token = token
        self.symbol = symbol
        self.name = name
        self.expiry = expiry
        self.strike = strike
        self.lotsize = lotsize
        self.instrumenttype = instrumenttype
        self.exch_seg = exch_seg
        self.tick_size = tick_size

    def get(self):
        return self

class TickerDetails:

    def __init__(self):
        get_file_dir = os.path.dirname(__file__)
        db_file = os.path.join(get_file_dir, 'static_db.db')
        self.conn = sqlite3.connect(db_file)

    def drop_angel_symbol_token_mapping_tables(self, exchange):
        drop_table = 'drop table if exists symbol_token_{exchange}_map'
        self.conn.execute(drop_table.format(exchange=exchange))
        self.conn.commit()

    def load_data_into_symbol_token_map(self):
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        r = requests.get(url)
        dataframe = pd.DataFrame(r.json())
        splits = list(dataframe.groupby("exch_seg"))
        for i in splits:
            exch_seg = i[0]
            self.drop_angel_symbol_token_mapping_tables(exch_seg)
            table_name = 'symbol_token_{exchange}_map'.format(exchange=exch_seg.lower())
            i[1].to_sql(table_name, self.conn, if_exists='replace', index=False)
        self.conn.commit()

    def get_token_info(self, symbol, exchange):
        select_query = 'SELECT token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size from symbol_token_{exchange}_map where symbol = "{symbol}"'
        cursor = self.conn.execute(select_query.format(exchange=exchange.lower(), symbol=symbol))
        for row in cursor:
            if row:
                obj = TickerInfo(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]).get()
                return obj
            else:
                return None

    def get_symbol_info(self, token, exchange):
        select_query = 'SELECT token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size from symbol_token_{exchange}_map where token = "{token}"'
        cursor = self.conn.execute(select_query.format(exchange=exchange.lower(), token=token))
        for row in cursor:
            if row:
                obj = TickerInfo(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]).get()
                return obj
            else:
                return None

if __name__ == '__main__':
    obj = TickerDetails()
    obj.get_symbol_info(228530, 'MCX')