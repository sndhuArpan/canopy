import datetime
import threading
import time
import os
import sys
import traceback
import pathlib

sys.path.append('/home/ec2-user/canopy/canopy')
sys.path.append('/Users/Sandhu/canopy/canopy/')
sys.path.append('/Users/Sandhu/canopy/canopy/src')

from datetime import datetime, timedelta
from src.DB.market_data.Market_Data import MarketData, LtpPriceModel
from src.DB.static_db.TickerDetails import TickerDetails
from Logging.Logger import GetLogger
from src.DB.static_db.BrokerAppDetails import BrokerAppDetails


class MarketDataWebSocketFallback:

    def __init__(self):
        logger_dir = os.path.join(pathlib.Path(__file__).parents[2], 'Log/MarketData')
        date_str = datetime.now().strftime("%d%m%Y")
        log_file_name = 'market_data_' + date_str + '.log'
        log_file = os.path.join(logger_dir, log_file_name)
        self.logger = GetLogger(log_file).get_logger()

    @staticmethod
    def update_ltp_in_market_date(token, exchange, ltp, ltt):
        model = LtpPriceModel().initialize(token, exchange)
        model.ltp_price = ltp
        model.ltp_time = ltt
        model.volume = None
        MarketData().update_ltp(model)

    def get_ltp_price_fallback(self, set_none=False):
        connection = BrokerAppDetails().get_normal_connection('S705342')
        register_token = MarketData().get_all_register_token()
        token_details = []
        for item in register_token:
            symbol = TickerDetails().get_symbol_info(item[0], item[1]).symbol
            item.append(symbol)
            token_details.append(item)
        for item in token_details:
            if set_none:
                MarketDataWebSocketFallback.update_ltp_in_market_date(item[0], item[1], None, None)
            else:
                try:
                    data_dict = connection.ltpData(exchange=item[1], tradingsymbol=item[2], symboltoken=item[0])
                    MarketDataWebSocketFallback.update_ltp_in_market_date(item[0], item[1],
                                                                          data_dict.get('data').get('ltp'),
                                                                          datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                    #MarketData().auto_deregister_token()
                except Exception as e:
                    self.logger.error('Exception : {0}\n{1}'.format(str(e), traceback.format_exc()))
                    time.sleep(1)
                    data_dict = connection.ltpData(exchange=item[1], tradingsymbol=item[2], symboltoken=item[0])
                    MarketDataWebSocketFallback.update_ltp_in_market_date(item[0], item[1],
                                                                          data_dict.get('data').get('ltp'),
                                                                          datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    def print_monitoring(self):
        while True:
            self.logger.info('*********   MONITORING LTP PRICE IN BACKGROUND   **********')
            time.sleep(60)

    def monitor_and_fallback(self):
        ltt = MarketData().get_max_last_traded_time()
        if ltt is not None:
            last_trade_time = datetime.strptime(ltt, '%d/%m/%Y %H:%M:%S')
            if last_trade_time < (datetime.now() - timedelta(seconds=20)):
                #checking if last_trade_time is older than 60 sec
                if last_trade_time < (datetime.now() - timedelta(seconds=60)):
                    self.logger.error('@@@@@@@@@@@      ERROR       @@@@@@@@@@@')
                    self.logger.error('@@@@@@@@@@    KILL PROCESS    @@@@@@@@@@@')
                    self.logger.error('@@@@@@@@@@ SEND TELEGRAM ALERT @@@@@@@@@@@')
                    self.logger.error('set ltp to NONE')
                    self.get_ltp_price_fallback(set_none = True)
                self.logger.info('Latest Price in MARKET_DATA table in older than 20 secs')
                self.logger.error('====>   Getting Latest price using fallback')
                self.get_ltp_price_fallback()


if __name__ == '__main__':
    fallback_obj = MarketDataWebSocketFallback()
    time.sleep(60)
    t = threading.Thread(target=fallback_obj.print_monitoring, daemon=True)
    t.start()
    while True:
        fallback_obj.monitor_and_fallback()



