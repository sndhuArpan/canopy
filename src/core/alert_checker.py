import os
import pathlib
import threading
import time
from datetime import datetime, timedelta

from Logging.Logger import GetLogger
from src.DB.market_data.Market_Data import MarketData, LtpPriceModel
from src.DB.static_db.TickerDetails import TickerDetails
from src.DB.static_db.alert_trigger import alert_trigger
from utils.Utils import interval_enum, Utils


class alert_checker:
    valid_interval = ['ONE_MINUTE', 'FIFTEEN_MINUTE', 'THIRTY_MINUTE', 'ONE_HOUR', 'ONE_DAY']

    def __init__(self):
        logger_dir = os.path.join(pathlib.Path.home(), 'Log/AlertChecker')
        date_str = datetime.now().strftime("%d%m%Y")
        log_file_name = 'AlertChecker' + date_str + '.log'
        log_file = os.path.join(logger_dir, log_file_name)
        self.logger = GetLogger(log_file).get_logger()
        self.stopTimestamp = Utils.getTimeOfToDay(16, 1, 0)
        self.alert_db = alert_trigger()
        self.market_data = MarketData()
        self.ticker_detail = TickerDetails()
        self.token_dict = {}

    def start_alert_checker(self):
        self.logger.info("alert checker started")
        self.alert_db.delete_triggered_alert()
        self.logger.info("triggered alert deleted")
        all_alert = self.alert_db.get_alert_for_interval()
        for Alert in all_alert:
            ticker_info = self.ticker_detail.get_token_info(Alert.symbol, 'nse')
            self.token_dict[Alert.symbol] = ticker_info.token
            ltp_model = LtpPriceModel().initialize(ticker_info.token, ticker_info.exch_seg)
            self.market_data.register_token(ltp_model)
        self.logger.info("all token are registered in market data")
        all_threads = []
        for interval in interval_enum:
            if interval.name in alert_checker.valid_interval:
                if interval.name == 'ONE_DAY':
                    p = threading.Thread(target=self.run_one_day_interval_threads,
                                         args=(interval,))
                    all_threads.append(p)
                else:
                    p = threading.Thread(target=self.run_intraday_interval_threads,
                                         args=(interval,))
                    all_threads.append(p)
        for job in all_threads:
            job.start()
        for job in all_threads:
            job.join()
        self.logger.info("alert checker completed")
        for token_info in self.token_dict:
            token = self.token_dict.get(token_info)
            self.market_data.deregister_token(token)

        self.logger.info("all token are deregistered")

    def run_intraday_interval_threads(self, interval):
        try:
            self.logger.info(f'In {interval.name} thread')
            multiplier = 1
            sleep_time = datetime.now().replace(minute=15, hour=9, second=0) + timedelta(minutes=interval.value*multiplier)
            waitSeconds = Utils.getEpoch(sleep_time) - Utils.getEpoch(datetime.now())
            if waitSeconds > 0:
                self.logger.info(f'sleeping for {int(waitSeconds/60)} minutes in {interval.name} thread')
                time.sleep(waitSeconds)
            multiplier = multiplier + 1
            while True:
                if datetime.now() > self.stopTimestamp:
                    break
                alerts = self.alert_db.get_alert_for_interval(interval.name)
                for interval_alert in alerts:
                    token = self.token_dict.get(interval_alert.symbol)
                    if token is None:
                        ticker_info = self.ticker_detail.get_token_info(interval_alert.symbol, 'nse')
                        self.token_dict[interval_alert.symbol] = ticker_info.token
                        ltp_model = LtpPriceModel().initialize(ticker_info.token, ticker_info.exch_seg)
                        self.market_data.register_token(ltp_model)
                        token = self.token_dict.get(interval_alert.symbol)

                    price = self.get_latest_price_websocket(token)
                    if price is None:
                        self.logger.info(f'price is None for {interval_alert.symbol} in  {interval.name} interval')
                        continue
                    if price >= float(interval_alert.price):
                        self.logger.info(f'alert triggered for {interval_alert.symbol} for {interval.name} interval')
                        interval_alert.triggered = '1'
                        self.alert_db.update_alert_trigger_status(interval_alert)
                        # send telegram

                sleep_time = datetime.now().replace(minute=15, hour=9, second=0) + timedelta(minutes=interval.value*multiplier)
                multiplier = multiplier + 1
                waitSeconds = Utils.getEpoch(sleep_time) - Utils.getEpoch(datetime.now())
                if waitSeconds > 0:
                    self.logger.info(f'sleeping for {int(waitSeconds/60)} minutes in {interval.name} thread')
                    time.sleep(waitSeconds)
        except Exception as e:
            self.logger.error(f'Exception occured for alert checker {interval.name} Thread -- {str(e)}')

    def run_one_day_interval_threads(self, interval):
        try:
            self.logger.info(f'In {interval.name} thread')
            sleep_time = datetime.now()
            sleep_time = sleep_time.replace(hour=15, minute=15, second=0)
            waitSeconds = Utils.getEpoch(sleep_time) - Utils.getEpoch(datetime.now())
            if waitSeconds > 0:
                self.logger.info(f'sleeping for {int(waitSeconds/60)} minutes in {interval.name} thread')
                time.sleep(waitSeconds)

            alerts = self.alert_db.get_alert_for_interval(interval.name)
            for interval_alert in alerts:
                token = self.token_dict.get(interval_alert.symbol)
                price = self.get_latest_price_websocket(token)
                if price >= float(interval_alert.price):
                    self.logger.info(f'alert triggered for {interval_alert.symbol} for {interval.name} interval')
                    interval_alert.triggered = '1'
                    self.alert_db.update_alert_trigger_status(interval_alert)
                    # send telegram
        except Exception as e:
            self.logger.error(f'Exception occured for alert checker {interval.name} Thread -- {str(e)}')

    def get_latest_price_websocket(self, token):
        return self.market_data.get_market_data(token).ltp_price


if __name__ == '__main__':
    alert = alert_checker()
    alert.start_alert_checker()
