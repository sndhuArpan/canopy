import sqlite3
import os
import calendar
from datetime import datetime
from dateutil import relativedelta
import requests
import pandas as pd

from src.DB.static_db.static_db import static_db


class ClientStrategyInfo(static_db):

    def create_table_strategy_client_map(self):
        create_table = '''create table strategy_client_map(strategy_name varchar2(30), 
                                                           client_id varchar2(30),
                                                           active_ind varchar(1))'''
        self.conn.execute(create_table)
        self.conn.commit()

    def insert_into_strategy_client_map(self, strategy_name, client_id):
        insert_query = '''insert into strategy_client_map(strategy_name, client_id, active_ind) values
                          ("{strategy_name}", "{client_id}", "Y")'''
        self.conn.execute(insert_query.format(strategy_name= strategy_name, client_id=client_id))
        self.conn.commit()

    def mark_strategy_as_inactive(self, strategy_name, client_id=None):
        if client_id is None:
            update_query = '''update strategy_client_map set active_ind = "N" 
                                where strategy_name = "{strategy_name}"'''.format(strategy_name= strategy_name)
        else:
            update_query = '''update strategy_client_map set active_ind = "N" 
                                where strategy_name = "{strategy_name}"
                                and   client_id = "{client_id}"'''.format(strategy_name= strategy_name, client_id=client_id)
        self.conn.execute(update_query)
        self.conn.commit()

    def mark_strategy_as_active(self, strategy_name, client_id=None):
        if client_id is None:
            update_query = '''update strategy_client_map set active_ind = "Y" 
                                where strategy_name = "{strategy_name}"'''.format(strategy_name= strategy_name)
        else:
            update_query = '''update strategy_client_map set active_ind = "Y" 
                                where strategy_name = "{strategy_name}"
                                and   client_id = "{client_id}"'''.format(strategy_name= strategy_name, client_id=client_id)
        self.conn.execute(update_query)
        self.conn.commit()

    def get_client_by_strategy(self, strategy_name):
        select_query = '''select client_id from strategy_client_map where active_ind = "Y"
                          and  strategy_name = "{strategy_name}"'''.format(strategy_name= strategy_name)
        cursor = self.conn.execute(select_query)
        client_id_list = []
        for row in cursor:
            if row:
                client_id_list.append(row[0])
        return client_id_list


if __name__ == '__main__':
    #ClientStrategyInfo().create_table_strategy_client_map()
    print(ClientStrategyInfo().get_client_by_strategy('CurrencyStrategy_30'))