from src.DB.static_db.static_db import static_db


class stock_scanner_model:
    def __init__(self, token=None, name=None, scanner_name=None, time=None):
        self.token = token
        self.name = name
        self.scanner_name = scanner_name
        self.time = time


class stock_scanner_db(static_db):

    def create_table_daily(self):
        create_table = 'Create table stock_scanner ' + '''(token varchar(10) NOT NULL,
                    name       varchar(10) NOT NULL,
                    scanner_name   varchar(10) NOT NULL,
                    time   varchar(36) NOT NULL);'''
        self.conn.execute(create_table)
        self.conn.commit()
        self.conn.close()

    def __insert_table_query(self):
        insert_query = 'INSERT INTO stock_scanner (token, name,scanner_name, time)' \
                       'values("{token}", "{name}","{scanner_name}", ' \
                       '"{time}") '
        return insert_query

    def insert_scanned_stocks(self, model_list, scanner_name):
        delete_query = 'delete from stock_scanner where scanner_name = "' + scanner_name + '"'
        self.conn.execute(delete_query)
        for model in model_list:
            query = self.__insert_table_query().format(token=model.token,
                                                       name=model.name,
                                                       scanner_name=model.scanner_name,
                                                       time=model.time)
            self.conn.execute(query)
        self.conn.commit()
