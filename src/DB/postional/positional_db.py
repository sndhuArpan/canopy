import enum
import sqlite3
import os
import pathlib

from pandas import DataFrame


class trade_status(enum.Enum):
    CREATED = 'CREATED'
    FIVE_MIN_BOUGHT_INITIATED = 'FIVE_MIN_BOUGHT_INITIATED'
    FIVE_MIN_BOUGHT = 'FIVE_MIN_BOUGHT'
    ACTIVE_INITIATED = 'ACTIVE_INITIATED'
    ACTIVE = 'ACTIVE'
    HALF_BOOK = 'HALF_BOOK'
    HALF_BOOKING = 'HALF_BOOKING'
    COMPLETED = 'COMPLETED'
    SELLING = 'SELLING'


class positional_model:
    def __init__(self, symbol=None, entry_price=None, client_id=None):
        self.id = 0
        self.symbol = symbol
        self.entry_price = entry_price
        self.qty = 0
        self.stoploss = 0.0
        self.fill_price = 0.0
        self.half_book_price = 0.0
        self.remaining_qty = 0
        self.status = trade_status.CREATED.name
        self.exit_price_one = 0.0
        self.exit_price_sec = 0.0
        self.client_id = client_id

    def get_positional_model(self):
        return self

    def to_dict(self):
        return {"id": self.id, "symbol": self.symbol, "entry_price": self.entry_price,
                "qty": self.qty, "stoploss": self.stoploss,
                "fill_price": self.fill_price, "half_book_price": self.half_book_price,
                "remaining_qty": self.remaining_qty, "status": self.status, "exit_price_one": self.exit_price_one,
                "exit_price_sec": self.exit_price_sec,
                "client_id": self.client_id}


class positional_db:

    def __init__(self):
        get_file_dir = os.path.dirname(__file__)
        db_file = os.path.join(get_file_dir, '../../../db_files/positional.db')
        self.conn = sqlite3.connect(db_file)

    def create_table(self):
        create_table = 'Create table positional_trades ' + '''(id INTEGER PRIMARY KEY,
                 symbol       varchar(10) NOT NULL,
                 entry_price   REAL NOT NULL,
                 qty        SMALLINT,
                 stoploss      REAL,
                 fill_price  REAL,
                 half_book_price       REAL,
                 remaining_qty       SMALLINT ,
                 status       varchar(10) NOT NULL,
                 exit_price_one       REAL,
                 exit_price_sec       REAL,
                 client_id    varchar(10) NOT NULL);'''
        self.conn.execute(create_table)
        self.conn.commit()
        self.conn.close()

    def select_all_tables(self):
        select_query = 'SELECT tbl_name FROM sqlite_master WHERE type="table"'
        cursor = self.conn.execute(select_query)
        table_names = []
        for row in cursor:
            table_names.append(row[0])
        return table_names

    def select_table_as_dataframe(self, table_name):
        select_query = 'select * from ' + table_name
        cursor = self.conn.execute(select_query)
        df = DataFrame(cursor.fetchall())
        if df.empty:
            return DataFrame()
        columns_list = []
        for i in cursor.description:
            columns_list.append(i[0])
        df.columns = columns_list
        return df

    def insert_trade(self, model):
        insert_query = f'INSERT INTO positional_trades (symbol, entry_price,status, client_id) values(' \
                       f'"{model.symbol}",{model.entry_price},"{model.status}","{model.client_id}")'
        self.conn.execute(insert_query)
        self.conn.commit()

    def __select_columns(self):
        return ' id,symbol,entry_price,qty,stoploss,fill_price,half_book_price,remaining_qty,status,exit_price_one,exit_price_sec,client_id '

    def __convert_row_model_list(self, cursor):
        model_list = []
        for row in cursor:
            model = positional_model()
            model.id = row[0]
            model.symbol = row[1]
            model.entry_price = row[2]
            model.qty = row[3]
            model.stoploss = row[4]
            model.fill_price = row[5]
            model.half_book_price = row[6]
            model.remaining_qty = row[7]
            model.status = row[8]
            model.exit_price_one = row[9]
            model.exit_price_sec = row[10]
            model.client_id = row[11]
            model_list.append(model)
        return model_list

    def __convert_row_model(self, cursor):
        model_list = []
        for row in cursor:
            model = positional_model()
            model.id = row[0]
            model.symbol = row[1]
            model.entry_price = row[2]
            model.qty = row[3]
            model.stoploss = row[4]
            model.fill_price = row[5]
            model.half_book_price = row[6]
            model.remaining_qty = row[7]
            model.status = row[8]
            model.exit_price_one = row[9]
            model.exit_price_sec = row[10]
            model.client_id = row[11]
            model_list.append(model)
        if model_list:
            return model_list[0]
        else:
            return None

    def get_trade_by_id(self, id):
        select_query = f'select {self.__select_columns()} from positional_trades where id = {id}'
        cursor = self.conn.execute(select_query)
        return self.__convert_row_model(cursor)

    def get_trade_by_symbol_status(self, symbol, status_list):
        status_para = ','.join(['?'] * len(status_list))
        select_query = f'select {self.__select_columns()} from positional_trades where symbol = "{symbol}" and status in ({status_para})'
        cursor = self.conn.execute(select_query, status_list)
        return self.__convert_row_model_list(cursor)

    def get_trade_by_status(self, status_list):
        status_para = ','.join(['?'] * len(status_list))
        select_query = f'select {self.__select_columns()} from positional_trades where status in ({status_para})'
        cursor = self.conn.execute(select_query, status_list)
        return self.__convert_row_model_list(cursor)

    def delete_trade(self, id):
        delete_query = f'delete from positional_trades where id = {id}'
        self.conn.execute(delete_query)
        self.conn.commit()

    def update_trade_price(self, id, entry_price):
        update_query = f'update positional_trades set entry_price = {entry_price} where id = {id}'
        self.conn.execute(update_query)
        self.conn.commit()

    def update_execute_trade(self, id, qty, stoploss, fill_price, half_book_price, remaining_qty, status):
        update_query = f'update positional_trades set qty={qty}, stoploss={stoploss}, fill_price={fill_price},' \
                       f'half_book_price={half_book_price},remaining_qty={remaining_qty},status="{status}" where id = {id}'
        self.conn.execute(update_query)
        self.conn.commit()

    def update_half_book_trade(self, id, exit_price_one, remaining_qty, status):
        update_query = f'update positional_trades set exit_price_one={exit_price_one}, remaining_qty={remaining_qty}, status="{status}"' \
                       f'where id = {id}'
        self.conn.execute(update_query)
        self.conn.commit()

    def complete_trade(self, id, exit_price_sec, remaining_qty, status):
        update_query = f'update positional_trades set exit_price_sec={exit_price_sec}, remaining_qty={remaining_qty}, status="{status}"' \
                       f'where id = {id}'
        self.conn.execute(update_query)
        self.conn.commit()

    def update_trade_status(self, id, status):
        update_query = f'update positional_trades set status="{status}" where id = {id}'
        self.conn.execute(update_query)
        self.conn.commit()
