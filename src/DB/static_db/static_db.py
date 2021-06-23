import sqlite3
import os
from pandas import DataFrame


class static_db:

    def __init__(self):
        get_file_dir = os.path.dirname(__file__)
        db_file = os.path.join(get_file_dir, '../../../db_files/static_db.db')
        self.conn = sqlite3.connect(db_file)

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