import csv
import sqlite3
import os
import pathlib

from pandas import DataFrame

from utils.telegram import telegram


class trade_status_model:
    def __init__(self, strategy_name):
        self.strategy_name = strategy_name
        self.client_id = ''
        self.order_id = ''
        self.system_trade_id = ''
        self.strategy_trade_id = ''
        self.order_type = ''
        self.order_status = ''
        self.transaction_type = ''
        self.share_name = ''
        self.price = ''
        self.qty = ''
        self.fill_qty = ''
        self.stop_loss = ''
        self.fill_time = ''
        self.instrument_type = ''

    def initialize_values(self, **kwargs):
        if kwargs.get('client_id'):
            self.client_id = kwargs.get('client_id')
        if kwargs.get('order_id'):
            self.order_id = kwargs.get('order_id')
        if kwargs.get('system_trade_id'):
            self.system_trade_id = kwargs.get('system_trade_id')
        if kwargs.get('strategy_trade_id'):
            self.strategy_trade_id = kwargs.get('strategy_trade_id')
        if kwargs.get('order_type'):
            self.order_type = kwargs.get('order_type')
        if kwargs.get('order_status'):
            self.order_status = kwargs.get('order_status')
        if kwargs.get('transaction_type'):
            self.transaction_type = kwargs.get('transaction_type')
        if kwargs.get('share_name'):
            self.share_name = kwargs.get('share_name')
        if kwargs.get('qty'):
            self.qty = kwargs.get('qty')
        if kwargs.get('stop_loss'):
            self.stop_loss = kwargs.get('stop_loss')
        if kwargs.get('instrument_type'):
            self.instrument_type = kwargs.get('instrument_type')


class canopy_db:

    def __init__(self):
        get_file_dir = os.path.dirname(__file__)
        db_file = os.path.join(get_file_dir, '../../../db_files/canopy.db')
        self.conn = sqlite3.connect(db_file)

    def create_table_daily(self, strategy_name):
        create_table = 'Create table ' + strategy_name + '_Daily_Status ' + '''(client_id varchar(36) NOT NULL,
                 order_id       varchar(10),
                 system_trade_id   varchar(36) NOT NULL,
                 strategy_trade_id   varchar(36) NOT NULL,
                 order_type        varchar(10) NOT NULL,
                 order_status      varchar(10) NOT NULL,
                 transaction_type  varchar(10) NOT NULL,
                 share_name       varchar(10) NOT NULL,
                 price       varchar(10) ,
                 qty       varchar(10),
                 fill_qty       varchar(10),
                 stop_loss       varchar(10),
                 fill_time    varchar(10),
                 instrument_type    varchar(10));'''
        self.conn.execute(create_table)
        self.conn.commit()
        self.conn.close()

    def __insert_table_daily_query(self):
        insert_query = 'INSERT INTO {strategy_name}_Daily_Status (client_id, system_trade_id,strategy_trade_id, order_type,order_status,' \
                       'transaction_type,share_name,qty,stop_loss,instrument_type) values("{client_id}", "{system_trade_id}","{strategy_trade_id}", ' \
                       '"{order_type}", "{order_status}", "{transaction_type}", "{share_name}", "{qty}", "{stop_loss}", "{instrument_type}") '
        return insert_query

    def insert_strategy_daily(self, model):
        query = self.__insert_table_daily_query().format(strategy_name=model.strategy_name,
                                                         client_id=model.client_id,
                                                         system_trade_id=model.system_trade_id,
                                                         strategy_trade_id=model.strategy_trade_id,
                                                         order_type=model.order_type,
                                                         order_status=model.order_status,
                                                         transaction_type=model.transaction_type,
                                                         share_name=model.share_name,
                                                         qty=model.qty,
                                                         stop_loss=model.stop_loss,
                                                         instrument_type=model.instrument_type)
        self.conn.execute(query)
        self.conn.commit()

    def update_daily_entry(self, model):
        update_query = 'Update ' + model.strategy_name + '_Daily_Status set'
        if model.order_id:
            update_query = update_query + ' order_id ="' + model.order_id + '",'
        if model.order_status:
            update_query = update_query + ' order_status ="' + model.order_status + '",'
        update_query = update_query[0:update_query.__len__() - 1] + ' where  system_trade_id = "' + str(
            model.system_trade_id) + '"'
        self.conn.execute(update_query)
        self.conn.commit()

    def update_daily_entry_status(self, model):
        update_query = 'Update ' + model.strategy_name + '_Daily_Status set'
        if model.order_status:
            update_query = update_query + ' order_status ="' + model.order_status + '"'
        update_query = update_query + ' where  system_trade_id = "' + str(model.system_trade_id) + '"'
        self.conn.execute(update_query)
        self.conn.commit()

    def update_daily_entry_filled(self, model):
        update_query = 'Update ' + model.strategy_name + '_Daily_Status set'
        if model.fill_qty:
            update_query = update_query + ' fill_qty ="' + str(model.fill_qty) + '",'
        if model.order_status:
            update_query = update_query + ' order_status ="' + model.order_status + '",'
        if model.fill_time:
            update_query = update_query + ' fill_time ="' + model.fill_time + '",'
        if model.price:
            update_query = update_query + ' price ="' + str(model.price) + '",'
        update_query = update_query[0:update_query.__len__() - 1] + ' where  system_trade_id = "' + str(model.system_trade_id) + '"'
        self.conn.execute(update_query)
        self.conn.commit()

    def __select_columns(self):
        return ' client_id,order_id,system_trade_id,strategy_trade_id,order_type,order_status,transaction_type,share_name,qty,fill_qty,stop_loss,fill_time,price '

    def __convert_row_model_list(self, cursor, strategy_name):
        model_list = []
        for row in cursor:
            model = trade_status_model(strategy_name)
            model.client_id = row[0]
            model.order_id = row[1]
            model.system_trade_id = row[2]
            model.strategy_trade_id = row[3]
            model.order_type = row[4]
            model.order_status = row[5]
            model.transaction_type = row[6]
            model.share_name = row[7]
            model.qty = row[8]
            model.fill_qty = row[9]
            model.stop_loss = row[10]
            model.fill_time = row[11]
            model.price = row[12]
            model_list.append(model)
        return model_list

    def __convert_row_model(self, cursor, strategy_name):
        model_list = []
        for row in cursor:
            model = trade_status_model(strategy_name)
            model.client_id = row[0]
            model.order_id = row[1]
            model.system_trade_id = row[2]
            model.strategy_trade_id = row[3]
            model.order_type = row[4]
            model.order_status = row[5]
            model.transaction_type = row[6]
            model.share_name = row[7]
            model.qty = row[8]
            model.fill_qty = row[9]
            model.stop_loss = row[10]
            model.fill_time = row[11]
            model.price = row[12]
            model_list.append(model)
        if model_list:
            return model_list[0]
        else:
            return None

    def select_daily_entry_system_trade_id(self, system_trade_id, strategy_name):
        select_query = 'select' + self.__select_columns() + ' from ' + strategy_name + '_Daily_Status where system_trade_id = "' \
                                                                                       '' + str(system_trade_id) + '"'
        cursor = self.conn.execute(select_query)
        return self.__convert_row_model(cursor, strategy_name)

    def select_daily_entry_order_id(self, order_id, strategy_name):
        select_query = 'select' + self.__select_columns() + ' from ' + strategy_name + '_Daily_Status where order_id = ' + str(
            order_id)
        cursor = self.conn.execute(select_query)
        return self.__convert_row_model(cursor, strategy_name)

    def select_daily_entry_strategy_trade_id(self, strategy_trade_id, strategy_name):
        select_query = 'select' + self.__select_columns() + ' from ' + strategy_name + '_Daily_Status where strategy_trade_id = ' + str(
            strategy_trade_id)
        cursor = self.conn.execute(select_query)
        return self.__convert_row_model_list(cursor, strategy_name)

    def select_daily_entry_client_id(self, client_id, strategy_name):
        select_query = 'select' + self.__select_columns() + ' from ' + strategy_name + '_Daily_Status where client_id = ' + client_id
        cursor = self.conn.execute(select_query)
        return self.__convert_row_model_list(cursor, strategy_name)

    def select_daily_entry_client_id_strategy_trade_id(self, strategy_trade_id, client_id, strategy_name):
        select_query = 'select' + self.__select_columns() + ' from ' + strategy_name + '_Daily_Status where strategy_trade_id = ' \
                                                                                       '' + str(
            strategy_trade_id) + ' and client_id = ' + client_id
        cursor = self.conn.execute(select_query)
        return self.__convert_row_model_list(cursor, strategy_name)

    def select_daily_entry_strategy(self, strategy_name):
        select_query = 'select' + self.__select_columns() + ' from ' + strategy_name + '_Daily_Status'
        cursor = self.conn.execute(select_query)
        return self.__convert_row_model_list(cursor, strategy_name)

    def select_daily_entry_client_id_not_order_status(self, client_id, strategy_name, order_status_list):
        select_query = 'select' + self.__select_columns() + ' from ' + strategy_name + '_Daily_Status where client_id = "' \
                                                                                       '' + client_id + '" and order_status not in (' + order_status_list + ')'
        cursor = self.conn.execute(select_query)
        return self.__convert_row_model_list(cursor, strategy_name)

    def select_distinct_client_id(self, strategy_name):
        select_query = 'select DISTINCT client_id from ' + strategy_name + '_Daily_Status'
        cursor = self.conn.execute(select_query)
        client_list = []
        for row in cursor:
            client_list.append(row[0])
        return client_list

    def create_csv(self, strategy_name, delete=False):
        select_query = 'select * from ' + strategy_name + '_Daily_Status'
        cursor = self.conn.execute(select_query)
        df = DataFrame(cursor.fetchall())
        if df.empty:
            return
        columns_list = []
        for i in cursor.description:
            columns_list.append(i[0])
        df.columns = columns_list
        df = df.loc[df['order_status'] == 'complete']
        get_file_dir = os.path.join(pathlib.Path.home(), 'trade_csv')
        csv_file_path = os.path.join(get_file_dir, strategy_name+'_trades.csv')
        if os.path.isdir(get_file_dir):
            if os.path.exists(csv_file_path):
                df.to_csv(csv_file_path, mode='a', header=False)
            else:
                df.to_csv(csv_file_path)
        else:
            os.mkdir(get_file_dir)
            df.to_csv(csv_file_path)
        telegram.send_file(csv_file_path)
        if delete:
            delete_query = 'delete from ' + strategy_name + '_Daily_Status'
            self.conn.execute(delete_query)
            self.conn.commit()


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



