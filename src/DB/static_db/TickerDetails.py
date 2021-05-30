import sqlite3
import os
import calendar
from datetime import datetime
from dateutil import relativedelta
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

    @staticmethod
    def return_ticker(row):
        if row:
            obj = TickerInfo(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]).get()
            return obj
        else:
            return None

    def get_token_info(self, symbol, exchange):
        select_query = 'SELECT token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size from symbol_token_{exchange}_map where symbol = "{symbol}"'
        cursor = self.conn.execute(select_query.format(exchange=exchange.lower(), symbol=symbol))
        for row in cursor:
            return TickerDetails.return_ticker(row)

    def get_symbol_info(self, token, exchange):
        select_query = 'SELECT token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size from symbol_token_{exchange}_map where token = "{token}"'
        cursor = self.conn.execute(select_query.format(exchange=exchange.lower(), token=token))
        for row in cursor:
            return TickerDetails.return_ticker(row)

    def get_nse_future_token(self, symbol, month_offset = 0):
        if month_offset == 0:
            month = datetime.now().strftime('%h').upper()
        else:
            month = (datetime.now()+ relativedelta.relativedelta(months=month_offset)).strftime('%h').upper()
        select_query = '''SELECT symbol_token_nfo_map.* from symbol_token_nfo_map join symbol_token_nse_map 
                          on symbol_token_nfo_map.name = symbol_token_nse_map.name
                          where symbol_token_nse_map.symbol = "{symbol}"
                          and symbol_token_nfo_map.instrumenttype like "FUT%"
                          and symbol_token_nfo_map.expiry like "%{month}%"'''
        cursor = self.conn.execute(select_query.format(symbol = symbol, month = month))
        for row in cursor:
            return TickerDetails.return_ticker(row)

    @staticmethod
    def get_option_strike_offset(option_type, strike):
        if strike == 'ITM':
            if option_type == 'CE':
                offset = 1
            else:
                offset = 2
        elif strike == 'OTM':
            if option_type == 'CE':
                offset = 2
            else:
                offset = 1
        else:
            offset = 0
        return offset

    def _get_all_expiry(self, symbol):
        select_query = 'select distinct symbol_token_nfo_map.expiry  from  symbol_token_nfo_map join symbol_token_nse_map on symbol_token_nfo_map.name = symbol_token_nse_map.name where symbol_token_nse_map.symbol = "{symbol}"'
        cursor = self.conn.execute(select_query.format(symbol=symbol))
        expiry_list = []
        for row in cursor:
            expiry_list.append(datetime.strptime(row[0], '%d%b%Y'))
        expiry_list.sort()
        return expiry_list

    def get_monthly_expiry_for_symbol(self, symbol, monthly_expiry_offset=0):
        curr_date = datetime.now()
        expiry_list = self._get_all_expiry(symbol)
        df = pd.DataFrame({'LoadedDate': expiry_list})
        month = df.groupby(df.LoadedDate - pd.offsets.MonthEnd()).last().reset_index(drop=True)
        month_ends = month['LoadedDate'].to_list()
        all_valid_monthly_expiry = [x for x in month_ends if curr_date < x ]
        return all_valid_monthly_expiry[monthly_expiry_offset].strftime('%d%b%Y').upper()

    def get_weekly_expiry_for_symbol(self, symbol, weekly_expiry_offset=0):
        curr_date = datetime.now()
        expiry_list = self._get_all_expiry(symbol)
        #check weekly expiry exists
        week_counts = 0
        next_month_expiry = []
        for expiry in expiry_list:
            if curr_date + relativedelta.relativedelta(months=1) > expiry > curr_date:
                week_counts = week_counts + 1
                next_month_expiry.append(expiry)
        if week_counts < 3:
            return None
        else:
            return next_month_expiry[weekly_expiry_offset].strftime('%d%b%Y').upper()

    def get_nse_option_token(self, symbol, option_type, ltp, strike='ATM', expiry_type='MONTHLY', offset=0):
        if expiry_type == 'WEEKLY':
            expiry = self.get_weekly_expiry_for_symbol(symbol, offset)
        else:
            expiry = self.get_monthly_expiry_for_symbol(symbol, offset)
        price_offset = TickerDetails.get_option_strike_offset(option_type, strike)
        select_query = '''select * from 
                            (SELECT symbol_token_nfo_map.*, 
                                substr(substr(replace(replace(symbol_token_nfo_map.symbol, symbol_token_nfo_map.name, ""), substr(symbol_token_nfo_map.expiry, 0,6), ""), -2, -10), 3, 10) as strike_price,
                                substr(symbol_token_nfo_map.symbol, -2, 10) as option_type 
                                from symbol_token_nfo_map join symbol_token_nse_map on symbol_token_nfo_map.name = symbol_token_nse_map.name
                                where symbol_token_nse_map.symbol = "{symbol}")
                          where option_type = "{option_type}"
                          and expiry = "{expiry}"
                          ORDER BY ABS(strike_price - {ltp})
                          LIMIT 1
                          OFFSET {price_offset}'''
        #print(select_query.format(symbol=symbol,expiry=expiry,option_type=option_type,ltp=ltp,price_offset=price_offset))
        cursor = self.conn.execute(select_query.format(symbol=symbol,
                                                       expiry=expiry,
                                                       option_type=option_type,
                                                       ltp=ltp,
                                                       price_offset=price_offset))
        for row in cursor:
            return TickerDetails.return_ticker(row)

if __name__ == '__main__':
    obj = TickerDetails()
    #ticker = obj.get_nse_future_token('MARUTI-EQ', 1)
    ticker = obj.get_nse_option_token('MARUTI-EQ', 'PE', 7000, 'ATM')
    print(ticker.symbol)
    #print(month_end_expiry)
