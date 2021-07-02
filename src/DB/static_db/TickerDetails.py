import sqlite3
import os
import calendar
from datetime import datetime
from dateutil import relativedelta
import requests
import pandas as pd

from src.DB.static_db.static_db import static_db


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


class TickerDetails(static_db):

    def create_table_ticker_details_load_date(self):
        create_table = '''create table ticker_details_load_date(load_date varchar2(10))'''
        self.conn.execute(create_table)
        self.conn.commit()

    def _get_latest_ticker_details_load_date(self):
        select_query = '''select * from ticker_details_load_date'''
        cursor = self.conn.execute(select_query)
        for row in cursor:
            if row:
                return row[0]

    def _update_insert_ticker_details_load_date(self):
        empty_table = '''delete from ticker_details_load_date'''
        self.conn.execute(empty_table)
        self.conn.commit()
        insert_latest_date = '''insert into ticker_details_load_date(load_date) values ("{latest_date}")'''
        latest_date = datetime.now().strftime('%d%m%Y')
        self.conn.execute(insert_latest_date.format(latest_date=latest_date))
        self.conn.commit()

    def drop_angel_symbol_token_mapping_tables(self, exchange):
        drop_table = 'drop table if exists symbol_token_{exchange}_map'
        self.conn.execute(drop_table.format(exchange=exchange))
        self.conn.commit()

    def load_data_into_symbol_token_map(self):
        latest_load_date = self._get_latest_ticker_details_load_date()
        if latest_load_date is None or datetime.strptime(latest_load_date, '%d%m%Y').date() < datetime.now().date():
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
            self._update_insert_ticker_details_load_date()
        else:
            pass

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

    def get_all_stocks(self, exchange):
        select_query = 'SELECT token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size from symbol_token_{exchange}_map'
        cursor = self.conn.execute(select_query.format(exchange=exchange.lower()))
        all_stocks = []
        for row in cursor:
            all_stocks.append(TickerDetails.return_ticker(row))
        return all_stocks

    @staticmethod
    def get_option_strike_offset(option_type, strike):
        if strike == 'ITM':
            if option_type == 'CE':
                offset = 1
            else:
                offset = 2
        elif strike == 'OTM':
            if option_type == 'PE':
                offset = 2
            else:
                offset = 1
        else:
            offset = 0
        return offset

    def _get_all_expiry(self, exchange, symbol, instrument_type):
        if exchange == 'CDS':
            select_query = 'select distinct symbol_token_cds_map.expiry  from  symbol_token_cds_map  where symbol_token_cds_map.name = "{symbol}" and symbol_token_cds_map.instrumenttype like "{instrument_type}%"'
        else:
            select_query = 'select distinct symbol_token_nfo_map.expiry  from  symbol_token_nfo_map join symbol_token_nse_map on symbol_token_nfo_map.name = symbol_token_nse_map.name where symbol_token_nse_map.symbol = "{symbol}" and symbol_token_nfo_map.instrumenttype like "{instrument_type}%"'
        cursor = self.conn.execute(select_query.format(symbol=symbol, instrument_type=instrument_type))
        expiry_list = []
        for row in cursor:
            if row[0] != "":
                expiry_list.append(datetime.strptime(row[0], '%d%b%Y'))
        expiry_list.sort()
        return expiry_list

    def get_monthly_expiry_for_symbol(self, exchange, instrument_type, symbol, monthly_expiry_offset=0):
        curr_date = datetime.now()
        expiry_list = self._get_all_expiry(exchange, symbol, instrument_type)
        df = pd.DataFrame({'LoadedDate': expiry_list})
        month = df.groupby(df.LoadedDate - pd.offsets.MonthEnd()).last().reset_index(drop=True)
        month_ends = month['LoadedDate'].to_list()
        all_valid_monthly_expiry = [x for x in month_ends if curr_date < x]
        if not all_valid_monthly_expiry:
            return None
        return all_valid_monthly_expiry[monthly_expiry_offset].strftime('%d%b%Y').upper()

    def get_weekly_expiry_for_symbol(self, exchange, instrument_type, symbol, weekly_expiry_offset=0):
        curr_date = datetime.now()
        expiry_list = self._get_all_expiry(exchange, symbol, instrument_type)
        # check weekly expiry exists
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

    def get_future_token(self, exchange, symbol, month_offset=0):
        expiry = self.get_monthly_expiry_for_symbol(exchange, 'FUT', symbol, month_offset)
        if exchange == 'CDS':
            select_query = '''SELECT symbol_token_cds_map.* from symbol_token_cds_map 
                              where symbol_token_cds_map.name = "{symbol}"
                              and symbol_token_cds_map.instrumenttype like "FUT%"
                              and symbol_token_cds_map.expiry = "{expiry}"
                            '''
        else:
            select_query = '''SELECT symbol_token_nfo_map.* from symbol_token_nfo_map join symbol_token_nse_map 
                              on symbol_token_nfo_map.name = symbol_token_nse_map.name
                              where symbol_token_nse_map.symbol = "{symbol}"
                              and symbol_token_nfo_map.instrumenttype like "FUT%"
                              and symbol_token_nfo_map.expiry = "{expiry}"'''
        cursor = self.conn.execute(select_query.format(symbol=symbol, expiry=expiry))
        for row in cursor:
            return TickerDetails.return_ticker(row)

    def get_option_token(self, exchange, symbol, option_type, ltp, expiry_type='MONTHLY', strike='ATM', offset=0):
        if expiry_type == 'WEEKLY':
            expiry = self.get_weekly_expiry_for_symbol(exchange, 'OPT', symbol, offset)
        else:
            expiry = self.get_monthly_expiry_for_symbol(exchange, 'OPT', symbol, offset)
        price_offset = TickerDetails.get_option_strike_offset(option_type, strike)
        if exchange == 'CDS':
            select_query = '''select * from 
                            (SELECT *, 
                               substr(substr(replace(symbol, name, ""), 6, 15), -2, -10) as strike_price ,
                                substr(symbol, -2, 10) as option_type 
                                from symbol_token_cds_map 
                                where symbol_token_cds_map.name = "{symbol}")
                          where option_type = "{option_type}"
                          and expiry = "{expiry}"
                          ORDER BY ABS(strike_price - {ltp})
                          LIMIT 1
                          OFFSET {price_offset}'''
        else:
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
        # print(select_query.format(symbol=symbol,expiry=expiry,option_type=option_type,ltp=ltp,price_offset=price_offset))
        cursor = self.conn.execute(select_query.format(symbol=symbol,
                                                       expiry=expiry,
                                                       option_type=option_type,
                                                       ltp=ltp,
                                                       price_offset=price_offset))
        for row in cursor:
            return TickerDetails.return_ticker(row)




if __name__ == '__main__':
    obj = TickerDetails()
    # print(obj._get_latest_ticker_details_load_date())
    # obj.load_data_into_symbol_token_map()
    # print(obj._get_latest_ticker_details_load_date())
    # ticker = obj.get_future_token('NSE', 'MARUTI-EQ')
    # print(ticker.symbol)
    # ticker = obj.get_option_token('NSE', 'MARUTI-EQ', 'PE', 7235, 'MONTHLY', 'OTM')
    # print(ticker.symbol, ticker.expiry)
    # ticker = obj.get_nse_future_token('MARUTI-EQ', 1)
    # ticker = obj.get_nse_option_token('MARUTI-EQ', 'PE', 7000, 'ATM')
    # print(ticker.symbol)
    # print(month_end_expiry)
