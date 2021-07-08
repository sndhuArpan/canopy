import math
import os
import pathlib
import threading
import time
from datetime import datetime, timedelta

from Logging.Logger import GetLogger
from src.DB.market_data.Market_Data import MarketData, LtpPriceModel
from src.DB.postional.positional_db import positional_db, trade_status
from src.DB.static_db.TickerDetails import TickerDetails
from src.models.Direction import Direction
from src.models.Duration import Duration
from src.models.Exchange import Exchange
from src.models.OrderStatus import OrderStatus
from src.models.Segment import Segment
from src.strategies.BaseStrategy import BaseStrategy
from src.models.ProductType import ProductType
from src.trademanager.Trade import Trade
from src.trademanager.TradeManager import TradeManager
from utils.Utils import Utils
from utils.telegram import telegram


def update_trade_status(trade_id, status):
    positional_db().update_trade_status(id=trade_id, status=status)


def get_trade_by_status(status):
    return positional_db().get_trade_by_status(status_list=status)


def complete_trade(id, exit_price_sec, remaining_qty, status):
    positional_db().complete_trade(id, exit_price_sec=exit_price_sec,
                                   remaining_qty=remaining_qty, status=status)


def update_half_book_trade(id, exit_price_one,
                           remaining_qty, status):
    positional_db().update_half_book_trade(id, exit_price_one=exit_price_one,
                                           remaining_qty=remaining_qty, status=status)


def update_execute_trade(id, qty, stoploss, fill_price,
                         half_book_price, remaining_qty,
                         status):
    positional_db().update_execute_trade(id=id, qty=qty, stoploss=stoploss, fill_price=fill_price,
                                         half_book_price=half_book_price, remaining_qty=remaining_qty,
                                         status=status)


class PositionalStrategy(BaseStrategy):
    __instance = None

    @staticmethod
    def getInstance():  # singleton class
        if PositionalStrategy.__instance is None:
            PositionalStrategy()
        return PositionalStrategy.__instance

    def __init__(self):
        if PositionalStrategy.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            PositionalStrategy.__instance = self
        # Call Base class constructor
        super().__init__("PositionalStrategy")
        # Initialize all the properties specific to this strategy

        logger_dir = os.path.join(pathlib.Path.home(), 'Log/PositionalStrategy')
        date_str = datetime.now().strftime("%d%m%Y")
        log_file_name = 'PositionalStrategy' + date_str + '.log'
        log_file = os.path.join(logger_dir, log_file_name)
        self.logger = GetLogger(log_file).get_logger()

        self.productType = ProductType.CNC
        self.exchange = Exchange.NSE
        self.startTimestamp = Utils.getTimeOfToDay(9, 15, 0)
        self.stopTimestamp = Utils.getTimeOfToDay(15, 16, 0)
        self.market_data = MarketData()
        self.ticker_detail = TickerDetails()
        self.token_dict = {}
        self.interval_higher = 45
        self.interval_smaller = 5
        self.per_trade_amount = 100
        self.per_trade_stop = 3
        self.per_trade_target = 5
        self.min_buy_percent = .20
        self.max_buy_percent = 3

    def process(self):
        all_trades = get_trade_by_status(['CREATED', 'ACTIVE', 'HALF_BOOK'])
        self.logger.info('Registering the Tokens')

        for trade in all_trades:
            if self.token_dict.get(trade.symbol) is None:
                self.get_token_and_register_symbol(trade.symbol)

        self.logger.info('All Token are Registered')
        monitor_thread = threading.Thread(target=self.start_monitoring,
                                          args=())
        half_book_thread = threading.Thread(target=self.start_Half_Book_thread,
                                            args=())
        stoploss_thread = threading.Thread(target=self.start_StopLoss_thread,
                                           args=())

        monitor_thread.start()
        half_book_thread.start()
        stoploss_thread.start()
        self.logger.info("Positional Threads Started")

        monitor_thread.join()
        half_book_thread.join()
        stoploss_thread.join()
        self.logger.info("Positional Completed")

        for token_info in self.token_dict:
            token = self.token_dict.get(token_info)
            self.market_data.deregister_token(token)

        self.logger.info("all token are deregistered")

    def start_monitoring(self):
        self.logger.info('In Monitoring Thread')
        multiplier = self.initialize_multiplier_low()
        while True:
            if datetime.now() > self.stopTimestamp:
                break
            if datetime.now() < Utils.getTimeOfToDay(10, 00, 0):  # this can also go to self
                self.logger.info('sleeping Thread')
                time.sleep(Utils.getEpoch(Utils.getTimeOfToDay(10, 00, 0)) - Utils.getEpoch(
                    datetime.now()))  # self of 10 AM time

            waitSeconds = self.get_next_small_interval(multiplier)
            if waitSeconds > 0:
                time.sleep(waitSeconds)
            multiplier = multiplier + 1

            all_monitor_trades = get_trade_by_status([trade_status.CREATED.name])
            for trade in all_monitor_trades:
                token = self.token_dict.get(trade.symbol)
                if token is None:
                    self.get_token_and_register_symbol(trade.symbol)
                    token = self.token_dict.get(trade.symbol)

                price = self.get_latest_price_websocket(token)
                if price is None:
                    self.logger.error(f'Price is None for {trade.symbol} in Monitoring thread')
                    continue
                min_buy_price = trade.entry_price + ((trade.entry_price * self.min_buy_percent) / 100)
                max_buy_price = trade.entry_price + ((trade.entry_price * self.max_buy_percent) / 100)
                if price > max_buy_price:
                    self.logger.info(
                        f'{trade.symbol} is canceled for client {trade.client_id} as ltp crosses {max_buy_price} in Monitoring thread')
                    update_trade_status(trade_id=trade.id, status=trade_status.CANCELED.name)
                if min_buy_price < price < max_buy_price:
                    self.logger.info(f'Entry price {price} triggered for {trade.symbol} in Monitoring thread')
                    threading.Thread(target=self.execute_five_min_buy_trade, args=(trade, price,)).start()

        self.logger.info('Monitoring Thread Completed')

    def execute_five_min_buy_trade(self, buy_trade, ltp):
        self.logger.info(f'In Execute Buy Thread for client {buy_trade.client_id}')
        update_trade_status(buy_trade.id, trade_status.FIVE_MIN_BOUGHT_INITIATED.name)
        qty = round(self.per_trade_amount / ltp)

        if qty < 2:
            qty = 2

        trade = Trade(tradingSymbol=buy_trade.symbol, symbolToken=self.token_dict.get(buy_trade.symbol),
                      clientId=buy_trade.client_id,
                      strategy_trade_id=buy_trade.id)
        trade.strategy = self.__class__.__name__
        trade.exchange = self.exchange
        trade.instrument_type = Segment.EQUITY
        trade.create_trade_orderType_market(Direction.BUY, qty, Duration.DAY, self.productType,
                                            ltp - ((ltp * self.per_trade_stop) / 100))
        self.placeTrade(trade)
        trade = self.trade_status(trade, buy_trade)
        if trade:
            fill_price = trade.price
            stoploss = fill_price - ((fill_price * self.per_trade_stop) / 100)
            target = fill_price + ((fill_price * self.per_trade_target) / 100)
            update_execute_trade(id=buy_trade.id, qty=trade.fill_qty, stoploss=stoploss, fill_price=fill_price,
                                 half_book_price=target, remaining_qty=trade.fill_qty,
                                 status=trade_status.FIVE_MIN_BOUGHT.name)

            telegram.send_text_client(
                f'{qty} of {buy_trade.symbol} are bought at price {fill_price} with stoploss of {stoploss}',
                buy_trade.client_id)
            self.logger.info(
                f'{qty} of {buy_trade.symbol} are bought at price {fill_price} with stoploss of {stoploss} for client {buy_trade.client_id}')

            now = datetime.now()
            newtime = now.replace(minute=int(now.minute / self.interval_higher) * self.interval_higher, second=0,
                                  microsecond=0) + timedelta(minutes=self.interval_higher)
            waitSeconds = Utils.getEpoch(newtime) - Utils.getEpoch(now)
            if waitSeconds > 0:
                time.sleep(waitSeconds)

            ltp = self.get_latest_price_websocket(self.token_dict.get(buy_trade.symbol))

            if ltp < buy_trade.entry_price:
                self.logger.info(f'5 min entry Failed for {buy_trade.symbol} for client {buy_trade.client_id}')
                telegram.send_text_client(
                    f'5 min entry Failed for {buy_trade.symbol} at {ltp} for client {buy_trade.client_id}',
                    buy_trade.client_id)
                buy_trade = positional_db().get_trade_by_id(buy_trade.id)
                self.sell_all_share(buy_trade)
            else:
                self.logger.info(f'5 min entry Active for {buy_trade.symbol} for client {buy_trade.client_id}')
                telegram.send_text_client(
                    f'5 min entry Active for {buy_trade.symbol} for client {buy_trade.client_id}',
                    buy_trade.client_id)
                update_trade_status(buy_trade.id, trade_status.ACTIVE.name)

    def start_Half_Book_thread(self):
        self.logger.info(f'In Half Book Thread')
        while True:
            if datetime.now() > self.stopTimestamp:
                break
            all_active_trades = get_trade_by_status([trade_status.ACTIVE.name])
            for trade in all_active_trades:
                token = self.token_dict.get(trade.symbol)
                if token is None:
                    self.get_token_and_register_symbol(trade.symbol)
                    token = self.token_dict.get(trade.symbol)

                price = self.get_latest_price_websocket(token)
                if price is None:
                    self.logger.error(f'price is None for {trade.symbol} in Target thread')
                    continue
                if price >= trade.half_book_price:
                    self.logger.info(f'Half Book price {price} triggered for {trade.symbol} in Target thread')
                    threading.Thread(target=self.half_book_share, args=(trade,)).start()

            time.sleep(10)
        self.logger.info(f'Half Book Thread Completed')

    def half_book_share(self, sell_trade):
        self.logger.info(f'In Half Booking Thread for client {sell_trade.client_id}')
        update_trade_status(sell_trade.id, trade_status.HALF_BOOKING.name)
        sell_qty = math.ceil(sell_trade.remaining_qty / 2)
        trade = Trade(tradingSymbol=sell_trade.symbol, symbolToken=self.token_dict.get(sell_trade.symbol),
                      clientId=sell_trade.client_id,
                      strategy_trade_id=sell_trade.id)
        trade.strategy = self.__class__.__name__
        trade.exchange = self.exchange
        trade.instrument_type = Segment.EQUITY
        trade.create_trade_orderType_market(Direction.SELL, sell_qty, Duration.DAY, self.productType,
                                            sell_trade.stoploss)
        self.placeTrade(trade)
        trade = self.trade_status(trade, sell_trade)
        if trade:
            exit_price_one = trade.price
            remaining_qty = sell_trade.remaining_qty - trade.fill_qty
            update_half_book_trade(sell_trade.id, exit_price_one=exit_price_one,
                                   remaining_qty=remaining_qty, status=trade_status.HALF_BOOK.name)

            telegram.send_text_client(
                f'{sell_qty} of {sell_trade.symbol} are Half Book at price {exit_price_one}', sell_trade.client_id)
            self.logger.info(
                f'{sell_qty} of {sell_trade.symbol} are Half Book at price {exit_price_one} for client {sell_trade.client_id}')

    def start_StopLoss_thread(self):
        self.logger.info('In StopLoss Thread')
        multiplier = self.initialize_multiplier_higher()
        while True:
            if datetime.now() > self.stopTimestamp:
                break
            waitSeconds = self.get_next_high_interval(multiplier)
            if waitSeconds > 0:
                time.sleep(waitSeconds)
            multiplier = multiplier + 1

            all_half_trades = get_trade_by_status(
                [trade_status.HALF_BOOK.name, trade_status.ACTIVE.name])
            for trade in all_half_trades:
                token = self.token_dict.get(trade.symbol)
                if token is None:
                    self.get_token_and_register_symbol(trade.symbol)
                    token = self.token_dict.get(trade.symbol)

                price = self.get_latest_price_websocket(token)
                if price is None:
                    self.logger.info(f'price is None for {trade.symbol} in StopLoss thread')
                    continue
                if price < trade.stoploss:
                    self.logger.info(
                        f'StopLoss triggered at {price} for {trade.symbol} for {trade.remaining_qty} quantities')
                    threading.Thread(target=self.sell_all_share, args=(trade,)).start()
        self.logger.info('StopLoss Thread Completed')

    def sell_all_share(self, sell_trade):
        # Thread check
        self.logger.info(f'In Sell Share Thread for client {sell_trade.client_id}')
        update_trade_status(sell_trade.id, trade_status.SELLING.name)
        sell_qty = sell_trade.remaining_qty
        trade = Trade(tradingSymbol=sell_trade.symbol, symbolToken=self.token_dict.get(sell_trade.symbol),
                      clientId=sell_trade.client_id,
                      strategy_trade_id=sell_trade.id)
        trade.strategy = self.__class__.__name__
        trade.exchange = self.exchange
        trade.instrument_type = Segment.EQUITY
        trade.create_trade_orderType_market(Direction.SELL, sell_qty, Duration.DAY, self.productType,
                                            sell_trade.stoploss)
        self.placeTrade(trade)
        trade = self.trade_status(trade, sell_trade)
        if trade:
            exit_price_sec = trade.price
            remaining_qty = sell_qty - trade.fill_qty
            complete_trade(sell_trade.id, exit_price_sec=exit_price_sec,
                           remaining_qty=remaining_qty, status=trade_status.COMPLETED.name)

            telegram.send_text_client(
                f'{sell_qty} of {sell_trade.symbol} are sell at price {exit_price_sec}', sell_trade.client_id)
            self.logger.info(
                f'{sell_qty} of {sell_trade.symbol} are sell at price {exit_price_sec} for client {sell_trade.client_id}')

    def get_next_high_interval(self, multiplier):
        sleep_time = datetime.now().replace(minute=15, hour=9, second=0) + timedelta(
            minutes=self.interval_higher * multiplier)
        return Utils.getEpoch(sleep_time) - Utils.getEpoch(datetime.now())

    def get_next_small_interval(self, multiplier):
        sleep_time = datetime.now().replace(minute=15, hour=9, second=0) + timedelta(
            minutes=self.interval_smaller * multiplier)
        return Utils.getEpoch(sleep_time) - Utils.getEpoch(datetime.now())

    def get_latest_price_websocket(self, token):
        return self.market_data.get_market_data(token).ltp_price

    def get_token_and_register_symbol(self, symbol):
        ticker_info = self.ticker_detail.get_token_info(symbol, 'nse')
        self.token_dict[symbol] = ticker_info.token
        ltp_model = LtpPriceModel().initialize(ticker_info.token, ticker_info.exch_seg)
        self.market_data.register_token(ltp_model)

    def placeTrade(self, trade):
        TradeManager().addNewTrade(trade)

    def initialize_multiplier_higher(self):
        now = datetime.now()
        fix = datetime.now().replace(minute=15, hour=9, second=0)
        if now <= fix:
            return 1
        else:
            diff = now - fix
            val = math.ceil((diff.seconds / 60) / self.interval_higher)
            if val == 0:
                return 1
            else:
                return val

    def initialize_multiplier_low(self):
        now = datetime.now()
        fix = datetime.now().replace(minute=15, hour=9, second=0)
        if now <= fix:
            return 1
        else:
            diff = now - fix
            val = math.ceil((diff.seconds / 60) / self.interval_smaller)
            if val == 0:
                return 1
            else:
                return val

    def trade_status(self, trade, positional_trade):
        while True:
            trade_model = TradeManager.get_trade('PositionalStrategy', trade.system_tradeID)
            if not trade_model:
                continue
            if trade_model.order_status == OrderStatus.COMPLETE:
                return trade_model
            if trade_model.order_status == OrderStatus.REJECTED:
                positional_db().update_trade_status(id=positional_trade.id, status=trade_status.REJECTED.name)
                self.logger.info(
                    f'Order for {trade.qty} quantities for {positional_trade.symbol} is Rejected for client {positional_trade.client_id}')
                telegram.send_text_client(
                    f'Order for {trade.qty} quantities for {positional_trade.symbol} is Rejected',
                    positional_trade.client_id)
                return None
            if trade_model.order_status == OrderStatus.FAILED:
                positional_db().update_trade_status(id=positional_trade.id, status=trade_status.FAILED.name)
                self.logger.info(
                    f'Order for {trade.qty} quantities for {positional_trade.symbol} is Failed for client {positional_trade.client_id}')
                telegram.send_text_client(
                    f'Order for {trade.qty} quantities for {positional_trade.symbol} is Failed',
                    positional_trade.client_id)
                return None
            if trade_model.order_status == OrderStatus.CANCELLED:
                positional_db().update_trade_status(id=positional_trade.id, status=trade_status.CANCELED.name)
                self.logger.info(
                    f'Order for {trade.qty} quantities for {positional_trade.symbol} is Cancelled for client {positional_trade.client_id}')
                telegram.send_text_client(
                    f'Order for {trade.qty} quantities for {positional_trade.symbol} is Cancelled',
                    positional_trade.client_id)
                return None


if __name__ == '__main__':
    PositionalStrategy().getInstance().run()
