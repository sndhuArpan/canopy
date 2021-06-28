from src.DB.static_db.static_db import static_db


class alert_trigger_model:
    def __init__(self, symbol=None, interval=None, price=None, triggered=None):
        self.symbol = symbol
        self.interval = interval
        self.price = price
        self.triggered = triggered


class alert_trigger(static_db):

    def create_table(self):
        create_table = 'Create table alert_trigger ' + '''(symbol varchar(10) NOT NULL,
                    interval       varchar(10) NOT NULL,
                    price   varchar(10) NOT NULL,
                    triggered   varchar(10) NOT NULL);'''
        self.conn.execute(create_table)
        self.conn.commit()
        self.conn.close()

    def __insert_table_query(self):
        insert_query = 'INSERT INTO alert_trigger (symbol, interval, price, triggered)' \
                       'values("{symbol}", "{interval}","{price}", ' \
                       '"{triggered}") '
        return insert_query

    def insert_alert(self, model):
        if self.check_trigger_present(model.symbol, model.interval):
            self.update_alert_trigger_price(model)
        else:
            query = self.__insert_table_query().format(symbol=model.symbol,
                                                       interval=model.interval,
                                                       price=model.price,
                                                       triggered=model.triggered)
            self.conn.execute(query)
            self.conn.commit()

    def get_alert_for_interval(self, interval=None):
        select_query = ''
        if interval is not None:
            select_query = 'select symbol, interval, price, triggered from alert_trigger where triggered = "0" and interval = "' + interval + '"'
        else:
            select_query = 'select symbol, interval, price, triggered from alert_trigger where triggered = "0"'
        cursor = self.conn.execute(select_query)
        stocks = []
        for row in cursor:
            alert = alert_trigger_model(row[0], row[1], row[2], row[3])
            stocks.append(alert)
        return stocks

    def update_alert_trigger_status(self, model):
        update_query = f'update alert_trigger set triggered = "{model.triggered}" where symbol = "{model.symbol}" and interval ="{model.interval}"'
        self.conn.execute(update_query)
        self.conn.commit()

    def update_alert_trigger_price(self, model):
        update_query = f'update alert_trigger set triggered = "{model.triggered}" ,  price = "{model.price}" where symbol = "{model.symbol}"' \
                       f' and interval="{model.interval}" and triggered = "0"'
        self.conn.execute(update_query)
        self.conn.commit()

    def check_trigger_present(self, symbol, interval):
        select_query = f'select * from alert_trigger where triggered = "0" and symbol ="{symbol}" and interval ="{interval}"'
        cursor = self.conn.execute(select_query)
        for row in cursor:
            return True
        return False

    def update_alert_trigger_token(self, symbol, token):
        update_query = f'update alert_trigger set token = "{token}" where symbol = "{symbol}"'
        self.conn.execute(update_query)
        self.conn.commit()

    def delete_triggered_alert(self):
        delete_query = 'delete from alert_trigger where triggered = "1"'
        self.conn.execute(delete_query)
        self.conn.commit()
