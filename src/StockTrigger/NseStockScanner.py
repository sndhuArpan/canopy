import os
import pathlib
from datetime import datetime

from Logging.Logger import GetLogger
from src.DB.market_data.Market_Data import MarketData
from src.DB.static_db.TickerDetails import TickerDetails
from src.DB.static_db.stock_scanner_db import stock_scanner_db, stock_scanner_model
from utils.Utils import interval_enum
from utils.telegram import telegram


class NseStockScanner:

    def __init__(self):
        logger_dir = os.path.join(pathlib.Path.home(), 'Log/NseStockScanner')
        date_str = datetime.now().strftime("%d%m%Y")
        log_file_name = 'NseStockScanner_' + date_str + '.log'
        log_file = os.path.join(logger_dir, log_file_name)
        self.logger = GetLogger(log_file).get_logger()
        self.last_day = 365
        self.last_high_day_max = 70
        self.last_high_day_min = 15
        self.fibo_low_level = 0.382
        self.fibo_high_level = 0.618
        self.static_db = TickerDetails().get_all_stocks('nse')
        self.market_data = MarketData()

    def find_stocks(self):
        valid_shares = {}
        self.logger.info('Scan Started')
        for stock_info in self.static_db:
            try:
                symbol = stock_info.symbol
                if '-EQ' not in symbol:
                    continue
                token = stock_info.token
                data = self.market_data.get_candle_data(interval=interval_enum.ONE_DAY,
                                                        share_symbol=token, exchange='NSE', candles=self.last_day)
                close_val = data['close'][data.index[-1]]
                close_vol = data['volume'][data.index[-1]]
                if not self.check_valid_share(close_val, close_vol):
                    continue
                self.logger.info('Scanning for ' + stock_info.name)
                max_high_value = 0
                max_high_index = 0
                max_low_value = 100000000
                is_valid_high = False
                if not data.empty:
                    high_values = data['high']
                    for index, value in enumerate(high_values):
                        if value >= max_high_value:
                            max_high_value = value
                            max_high_index = index

                    if len(data) - self.last_high_day_max <= max_high_index <= len(data) - self.last_high_day_min:
                        is_valid_high = True
                    else:
                        is_valid_high = False
                    if is_valid_high:
                        low_values = data['low']
                        for index, value in reversed(list(enumerate(low_values))):
                            if index > max_high_index:
                                if value <= max_low_value:
                                    max_low_value = value
                            else:
                                break
                        high_low_diff = max_high_value - max_low_value
                        fibbo_high_level = max_low_value + (high_low_diff * self.fibo_high_level)
                        fibbo_low_level = max_low_value + (high_low_diff * self.fibo_low_level)

                        if fibbo_high_level >= data['close'][data.index[-1]] >= fibbo_low_level:
                            valid_shares[stock_info.token] = 'NSE:' + stock_info.name
            except Exception as e:
                self.logger.error(str(e))

        self.logger.info("Scan Completed")
        self.logger.info(f'{str(len(valid_shares))} valid share found')
        str_valid_shares = ','.join(valid_shares.values())
        try:
            db = stock_scanner_db()
            model_list = []
            for valid_share in valid_shares:
                model = stock_scanner_model(token=valid_share, name=valid_shares[valid_share], scanner_name=self.__class__.__name__, time=datetime.now().date())
                model_list.append(model)
            db.insert_scanned_stocks(model_list=model_list, scanner_name=self.__class__.__name__)
        except Exception as e:
            self.logger.error(str(e))
        self.logger.info(str_valid_shares)
        telegram.send_text(str_valid_shares)

    def check_valid_share(self, close, vol):
        if close <= 100:
            return vol >= 500000
        if 101 <= close <= 500:
            return vol >= 200000
        if 501 <= close <= 2000:
            return vol >= 100000
        if 2000 <= close:
            return vol >= 50000


if __name__ == '__main__':
    nse = NseStockScanner()
    nse.find_stocks()
