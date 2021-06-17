import json
import logging
import os
import threading
import uuid
import time
import traceback
import pandas as pd

from datetime import datetime, timedelta

from src.DB.market_data.Market_Data import MarketData, LtpPriceModel
from src.DB.static_db.BrokerAppDetails import BrokerAppDetails
from src.DB.static_db.TickerDetails import TickerDetails
from src.DB.static_db.ClientStrategyInfo import ClientStrategyInfo
from src.models.Direction import Direction
from src.models.Duration import Duration
from src.models.Exchange import Exchange
from src.models.OrderStatus import OrderStatus
from src.models.ProductType import ProductType
from src.models.Segment import Segment
from src.strategies.BaseStrategy import BaseStrategy
from src.trademanager.Trade import Trade
from src.trademanager.TradeManager import TradeManager
from utils.Utils import Utils, interval_enum
from utils.telegram import telegram


class CurrencyStrategy_30(BaseStrategy):
    __instance = None

    @staticmethod
    def getInstance():  # singleton class
        if CurrencyStrategy_30.__instance is None:
            CurrencyStrategy_30()
        return CurrencyStrategy_30.__instance

    def __init__(self):
        if CurrencyStrategy_30.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CurrencyStrategy_30.__instance = self
        # Call Base class constructor
        super().__init__("CurrencyStrategy_30")
        # Initialize all the properties specific to this strategy
        self.productType = ProductType.NRML
        self.exchange = Exchange.CDS
        self.startTimestamp = Utils.getTimeOfToDay(9, 30, 0)
        self.stopTimestamp = Utils.getTimeOfToDay(15, 30, 0)
        self.squareOffTimestamp = Utils.getTimeOfToDay(12, 30, 0)

        self.quantity = 20
        self.symbol_token_dict = {}
        self.client_list = {}

        self.trade_dataframe = pd.DataFrame(columns=['client', 'buy_trade', 'sell_trade', 'sl_trade'])

        for client in ClientStrategyInfo().get_client_by_strategy(self.__class__.__name__):
            self.client_list[client] = uuid.uuid1()
            self.trade_dataframe = self.trade_dataframe.append({'client': client, 'buy_trade': 0,
                                                                'sell_trade': 0, 'sl_trade': 0},
                                                               ignore_index=True)

        self.trade_dataframe.index = self.trade_dataframe['client']
        self.max_sl_call = 2
        self.token_detail = TickerDetails().get_future_token(self.exchange, 'USDINR')
        # market db object
        self.market_data = MarketData()
        # Register Symbols
        ltp_model = LtpPriceModel().initialize(self.token_detail.token, self.token_detail.exch_seg)
        self.market_data.register_token(ltp_model)

    def process(self):
        self.one_pip = 0.0025
        data = self.market_data.get_ltp_data(self.exchange, self.token_detail.symbol, self.token_detail.token)
        high_range = data['high']
        low_range = data['low']
        buy_high_range = high_range + self.one_pip
        buy_sl = self.get_latest_price_websocket(self.token_detail.token) - 5 * self.one_pip
        sell_low_range = low_range - self.one_pip
        sell_sl = low_range + 5 * self.one_pip
        while True:
            if datetime.now() > self.stopTimestamp:
                break
            ltp_price = self.get_latest_price_websocket(self.token_detail.token)
            if ltp_price >= buy_high_range:
                self.squareOffTimestamp = datetime.now() + timedelta(hours=1)
                jobs = []
                for client_key in self.client_list:
                    p = threading.Thread(target=self.generateTrade_buy,
                                         args=(client_key, buy_sl, buy_high_range,))
                    jobs.append(p)

                for job in jobs:
                    job.start()

                for job in jobs:
                    job.join()
                print('done')
                break
            elif ltp_price <= sell_low_range:
                self.squareOffTimestamp = datetime.now() + timedelta(minutes=10)
                jobs = []
                for client_key in self.client_list:
                    p = threading.Thread(target=self.generateTrade_sell,
                                         args=(client_key, sell_sl, sell_low_range,))
                    jobs.append(p)

                for job in jobs:
                    job.start()

                for job in jobs:
                    job.join()
                break
            time.sleep(1)

        print('done')

    def get_latest_price_websocket(self, token):
        return self.market_data.get_market_data(token).ltp_price

    def generateTrade_buy(self, client, stop_loss, price):
        try:
            trade = Trade(tradingSymbol=self.token_detail.symbol, symbolToken=self.token_detail.token, clientId=client,
                          strategy_trade_id=self.client_list.get(client))
            trade.exchange = self.exchange
            trade.strategy = self.__class__.__name__
            trade.instrument_type = Segment.CURRENCY
            trade.create_trade_orderType_limit(Direction.BUY, self.quantity, price, Duration.DAY, self.productType,
                                               stop_loss)
            self.placeTrade(trade, client)

            start_time = self.next_five_min()

            fill_price = 0
            while True:
                trade_model = TradeManager.get_trade(self.__class__.__name__, trade.system_tradeID)
                if not trade_model:
                    continue
                if trade_model.order_status == OrderStatus.COMPLETE:
                    fill_price = float(trade_model.price)
                    break

            target = fill_price + 10 * self.one_pip
            remaining_qty = self.quantity
            half_sell = False
            sell_qty = 0
            while True:
                latest_ltp = self.get_latest_price_websocket(self.token_detail.token)
                sell_trade = False
                if datetime.now() < start_time:
                    if latest_ltp >= target and not half_sell:
                        sell_trade = True
                        sell_qty = self.quantity / 2
                        remaining_qty = remaining_qty - sell_qty
                        stop_loss = fill_price
                else:
                    if latest_ltp >= target and not half_sell:
                        sell_trade = True
                        sell_qty = self.quantity / 2
                        remaining_qty = remaining_qty - sell_qty
                        stop_loss = fill_price
                    elif latest_ltp <= stop_loss:
                        sell_trade = True
                        sell_qty = remaining_qty
                        remaining_qty = 0
                    elif datetime.now() > self.squareOffTimestamp:
                        sell_trade = True
                        sell_qty = remaining_qty
                        remaining_qty = 0
                if sell_trade:
                    trade = Trade(tradingSymbol=self.token_detail.symbol, symbolToken=self.token_detail.token,
                                  clientId=client,
                                  strategy_trade_id=self.client_list.get(client))
                    trade.strategy = self.__class__.__name__
                    trade.exchange = self.exchange
                    trade.instrument_type = Segment.CURRENCY
                    trade.create_trade_orderType_market(Direction.SELL, sell_qty, Duration.DAY, self.productType,
                                                        stop_loss)
                    self.placeTrade(trade, client)
                    if remaining_qty != 0:
                        half_sell = True
                    else:
                        break
                time.sleep(1)

        except:
            errorString = 'Exception occurred while generating trade for buy CurrencyStrategy_30 for client {client} , ---  {error}'.format(
                client=str(client),
                error=str(traceback.print_exc()))
            logging.error(errorString)
            telegram.send_text(errorString)

    def generateTrade_sell(self, client, stop_loss, price):
        try:
            trade = Trade(tradingSymbol=self.token_detail.symbol, symbolToken=self.token_detail.token, clientId=client,
                          strategy_trade_id=self.client_list.get(client))
            trade.exchange = self.exchange
            trade.strategy = self.__class__.__name__
            trade.instrument_type = Segment.CURRENCY
            trade.create_trade_orderType_limit(Direction.SELL, self.quantity, price, Duration.DAY, self.productType,
                                               stop_loss)
            self.placeTrade(trade, client)

            start_time = self.next_five_min()

            fill_price = 0
            while True:
                trade_model = TradeManager.get_trade(self.__class__.__name__, trade.system_tradeID)
                if not trade_model:
                    continue
                if trade_model.order_status == OrderStatus.COMPLETE:
                    fill_price = float(trade_model.price)
                    break

            target = fill_price - 10 * self.one_pip

            remaining_qty = self.quantity
            half_buy = False
            buy_qty = 0
            while True:
                latest_ltp = self.get_latest_price_websocket(self.token_detail.token)
                buy_trade = False
                if datetime.now() < start_time:
                    if latest_ltp <= target and not half_buy:
                        buy_trade = True
                        buy_qty = self.quantity / 2
                        remaining_qty = remaining_qty - buy_qty
                        stop_loss = fill_price
                else:
                    if latest_ltp <= target and not half_buy:
                        buy_trade = True
                        buy_qty = self.quantity / 2
                        remaining_qty = remaining_qty - buy_qty
                        stop_loss = fill_price
                    elif latest_ltp >= stop_loss:
                        buy_trade = True
                        buy_qty = remaining_qty
                        remaining_qty = 0
                    elif datetime.now() > self.squareOffTimestamp:
                        buy_trade = True
                        buy_qty = remaining_qty
                        remaining_qty = 0
                if buy_trade:
                    trade = Trade(tradingSymbol=self.token_detail.symbol, symbolToken=self.token_detail.token,
                                  clientId=client,
                                  strategy_trade_id=self.client_list.get(client))
                    trade.strategy = self.__class__.__name__
                    trade.exchange = self.exchange
                    trade.instrument_type = Segment.CURRENCY
                    trade.create_trade_orderType_market(Direction.BUY, buy_qty, Duration.DAY, self.productType,
                                                        stop_loss)
                    self.placeTrade(trade, client)
                    if remaining_qty != 0:
                        half_buy = True
                    else:
                        break
                time.sleep(1)
        except:
            errorString = 'Exception occurred while generating trade for sell CurrencyStrategy_30 for client {client} , ---  {error}'.format(
                client=str(client),
                error=str(traceback.print_exc()))
            logging.error(errorString)
            telegram.send_text(errorString)

    def placeTrade(self, trade, client):
        trade_df = self.trade_dataframe.loc[client]
        if trade.direction == Direction.BUY:
            if trade_df['buy_trade'] == self.max_buy_call:
                return None
            else:
                trade_df['buy_trade'] = trade_df['buy_trade'] + 1
        else:
            if trade_df['sell_trade'] == self.max_sl_call:
                return None
            else:
                trade_df['sell_trade'] = trade_df['sell_trade'] + 1
        if not self.incubation:
            return TradeManager().addNewTrade(trade)
        else:
            latest_ltp = self.get_latest_price_websocket(self.token_detail.token)
            trade.requestedEntry = latest_ltp
            return TradeManager().incubate_trade(trade)

    def next_five_min(self):
        now = datetime.now()
        newtime = now.replace(minute=int(now.minute / 5) * 5, second=0, microsecond=0) + timedelta(minutes=5)
        return newtime

    def sleep_next_fifteen_min(self):
        now = datetime.now()
        newtime = now.replace(minute=int(now.minute / 15) * 15, second=0, microsecond=0) + timedelta(minutes=15)
        waitSeconds = Utils.getEpoch(newtime) - Utils.getEpoch(now)
        if waitSeconds > 0:
            time.sleep(waitSeconds)
