import json
import logging
import math
import os
import uuid
import time
import multiprocessing
import pandas as pd

from datetime import datetime

from src.DB.static_db.TickerDetails import TickerDetails
from src.models.Duration import Duration
from src.models.OrderStatus import OrderStatus
from src.models.ProductType import ProductType
from src.models.Direction import Direction
from src.models.Exchange import Exchange
from src.models.Segment import Segment
from src.models.Variety import Variety
from src.strategies.BaseStrategy import BaseStrategy
from src.trademanager.Trade import Trade
from src.trademanager.TradeManager import TradeManager
from utils.Utils import Utils
from src.DB.market_data.Market_Data import MarketData, LtpPriceModel


# Each strategy has to be derived from BaseStrategy
class SampleStrategy(BaseStrategy):
    __instance = None

    @staticmethod
    def getInstance():  # singleton class
        if SampleStrategy.__instance == None:
            SampleStrategy()
        return SampleStrategy.__instance

    def __init__(self):
        if SampleStrategy.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SampleStrategy.__instance = self
        # Call Base class constructor
        super().__init__("SAMPLE")
        # Initialize all the properties specific to this strategy
        self.productType = ProductType.MIS
        self.exchange = Exchange.NSE
        self.symbols = ["IDEA-EQ"]
        self.startTimestamp = Utils.getTimeOfToDay(10, 30, 0)
        self.stopTimestamp = Utils.getTimeOfToDay(13, 10,
                                                  0)
        self.squareOffTimestamp = Utils.getTimeOfToDay(13, 30, 0)

        self.symbol_token_dict = {}
        self.client_list = {}
        self.trade_dataframe = pd.DataFrame(columns=['client', 'buy_trade', 'sell_trade', 'sl_trade'])
        self.trade_manager = TradeManager()
        tFile = open(os.path.abspath('src/data/client_strategy_map.py'), 'r')
        client_strategy_data = json.loads(tFile.read())['mapping']
        for i in client_strategy_data:
            if self.__class__.__name__ == i['strategy']:
                for client in i['client']:
                    self.client_list[client] = uuid.uuid1()
                    self.trade_dataframe = self.trade_dataframe.append({'client': client, 'buy_trade': 0,
                                                                        'sell_trade': 0, 'sl_trade': 0},
                                                                       ignore_index=True)
        self.trade_dataframe.index = self.trade_dataframe['client']
        self.token_detail = TickerDetails().get_token_info('IDEA-EQ', 'NSE')
        # market db object
        self.market_data = MarketData()
        # Register Symbols
        ltp_model = LtpPriceModel().initialize(self.token_detail.token, self.token_detail.exch_seg)
        self.market_data.register_token(ltp_model)


    def process(self):
        for i in self.symbols:
            jobs = []
            for client_key in self.client_list:
                p = multiprocessing.Process(target=self.generateTrade, args=(i, Direction.BUY, client_key,))
                jobs.append(p)
                p.start()

            for job in jobs:
                job.join()

    def get_ltp(self, token):
        return self.market_data.get_market_data(token)

    def generateTrade(self, tradingSymbol, direction, client_key):
        trade = Trade(tradingSymbol=tradingSymbol, symbolToken=self.token_detail.token, clientId=client_key,
                      strategy_trade_id=self.client_list.get(client_key))
        trade.strategy = self.__class__.__name__
        trade.instrument_type = Segment.EQUITY
        ltp = self.get_ltp(self.token_detail.token)
        stoploss = ltp - math.ceil((ltp * 1) / 100)
        trade.create_trade_orderType_market(direction, 1, Duration.DAY, self.productType, stoploss)
        orderId = self.placeTrade(trade, client_key)
        if orderId is None:
            return
        while True:
            trade_model = TradeManager.get_trade(self.__class__.__name__, trade.system_tradeID)
            if not trade_model:
                continue
            if trade_model.order_status == OrderStatus.COMPLETE:
                trade = Trade(tradingSymbol=tradingSymbol, symbolToken=self.token_detail.token, clientId=client_key,
                              strategy_trade_id=self.client_list.get(client_key))
                trade.strategy = self.__class__.__name__
                trade.instrument_type = Segment.EQUITY
                trade.create_trade_orderType_stoploss_market(Direction.SELL, 1, stoploss, Duration.DAY,
                                                             self.productType)
                self.placeTrade(trade, client_key)
                break

        now = datetime.now()
        if now < self.squareOffTimestamp:
            waitSeconds = Utils.getEpoch(self.squareOffTimestamp) - Utils.getEpoch(now)
            logging.info("%s: Waiting for %d seconds till startegy start timestamp reaches...", self.getName(),
                         waitSeconds)
            if waitSeconds > 0:
                time.sleep(waitSeconds)

        sl_trade_model = TradeManager.get_trade(self.__class__.__name__, trade.system_tradeID)
        sell_call = False
        if sl_trade_model.order_status != OrderStatus.COMPLETE:
            sell_call = True
            self.trade_manager().executeCancelTrade(sl_trade_model)

        if sell_call:
            trade = Trade(tradingSymbol=tradingSymbol, symbolToken=self.token_detail.token, clientId=client_key,
                          strategy_trade_id=self.client_list.get(client_key))
            trade.strategy = self.__class__.__name__
            trade.instrument_type = Segment.EQUITY
            trade.create_trade_orderType_market(Direction.SELL, 1, Duration.DAY, self.productType, stoploss)
            self.placeTrade(trade, client_key)

        while True:
            trade_model = TradeManager.get_trade(self.__class__.__name__, trade.system_tradeID)
            if not trade_model:
                continue
            if trade_model.order_status == OrderStatus.COMPLETE:
                break

    def placeTrade(self, trade, client):
        trade_df = self.trade_dataframe.loc[client]
        if trade.variety == Variety.STOPLOSS:
            if trade_df['sl_trade'] == self.max_sl_call:
                return None
            else:
                trade_df['sl_trade'] = trade_df['sl_trade'] + 1
        else:
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
            return self.trade_manager.addNewTrade(trade)
        else:
            return self.trade_manager.incubate_trade(trade)
