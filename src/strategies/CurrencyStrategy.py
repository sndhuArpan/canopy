import json
import logging
import math
import os
import uuid
import time
import multiprocessing
import pandas as pd

from datetime import datetime, timedelta

from Data_Wrappers.Indicators.EMA import EMA
from src.DB.market_data.Market_Data import MarketData, LtpPriceModel
from src.DB.static_db.TickerDetails import TickerDetails
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


class CurrencyStrategy(BaseStrategy):
    __instance = None

    @staticmethod
    def getInstance():  # singleton class
        if CurrencyStrategy.__instance is None:
            CurrencyStrategy()
        return CurrencyStrategy.__instance

    def __init__(self):
        if CurrencyStrategy.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CurrencyStrategy.__instance = self
        # Call Base class constructor
        super().__init__("CurrencyStrategy")
        # Initialize all the properties specific to this strategy
        self.productType = ProductType.MIS
        self.exchange = Exchange.CDS
        self.startTimestamp = Utils.getTimeOfToDay(10, 00, 0)
        self.stopTimestamp = Utils.getTimeOfToDay(15, 30, 0)
        self.squareOffTimestamp = Utils.getTimeOfToDay(16, 30, 0)

        self.quantity = 12
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

        self.token_detail = TickerDetails().get_future_token(self.exchange, 'USDINR')
        # market db object
        self.market_data = MarketData()
        # Register Symbols
        ltp_model = LtpPriceModel().initialize(self.token_detail.token, self.token_detail.exch_seg)
        # self.market_data.register_token(ltp_model)

    def process(self):
        in_watch = False
        in_buy_trade = False
        in_sell_trade = False
        ema_small = EMA(interval=23, on='close')
        ema_small_name = 'ema_23'
        ema_large = EMA(interval=53, on='close')
        ema_large_name = 'ema_53'
        while True:
            if datetime.now() >= self.stopTimestamp:
                break
            data = self.market_data.get_candle_data(interval=interval_enum.FIFTEEN_MINUTE,
                                                    share_symbol='3273', exchange='NSE')
            last_index = data.index[-1]
            high_range = data['high'][0]
            low_range = data['low'][0]
            mc_candle_idx = 0
            out = 0
            valid_count = 0
            for index in data.index:
                high_range = data['high'][index]
                low_range = data['low'][index]
                mc_candle_idx = index
                for i in range(index + 1, last_index):
                    if high_range >= data['open'][i] >= low_range and high_range >= data['close'][i] >= low_range:
                        valid_count = valid_count + 1
                    else:
                        valid_count = 0
                        break
                if i == last_index - 1:
                    break

            # if data['high'][idx] > high_range or data['low'][idx] < low_range:
            #     out = out + 1

            if valid_count >= 3:
                in_watch = True

            if in_watch:
                while True:
                    self.sleep_next_five_min()
                    small_data = self.market_data.get_candle_data(interval=interval_enum.FIVE_MINUTE,
                                                                  share_symbol='3273', exchange='NSE')
                    last_index = data.index[-1]
                    if small_data['high'][last_index] > high_range:
                        data_ind = self.get_candledata_indicator()
                        l_idx = data_ind.index[-1]
                        if data_ind[ema_large_name][l_idx] < data_ind[ema_small_name][l_idx] < data_ind['close'][l_idx]:
                            if data_ind['rsi'][l_idx] >= 58:
                                in_buy_trade = True
                        break
                    elif small_data['low'][last_index] < low_range:
                        data_ind = self.get_candledata_indicator()
                        l_idx = data_ind.index[-1]
                        if data_ind[ema_large_name][l_idx] > data_ind[ema_small_name][l_idx] > data_ind['close'][l_idx]:
                            if data_ind['rsi'][l_idx] <= 42:
                                in_sell_trade = True
                        break

            if in_buy_trade:
                jobs = []
                for client_key in self.client_list:
                    stoploss = high_range - 0.0025 * 7
                    p = multiprocessing.Process(target=self.generateTrade, args=(client_key, Direction.BUY, stoploss,))
                    jobs.append(p)
                    p.start()
                for job in jobs:
                    job.join()
                in_buy_trade = False
            if in_sell_trade:
                jobs = []
                for client_key in self.client_list:
                    stoploss = low_range + 0.0025 * 7
                    p = multiprocessing.Process(target=self.generateTrade, args=(client_key, Direction.SELL, stoploss,))
                    jobs.append(p)
                    p.start()
                for job in jobs:
                    job.join()
                in_sell_trade = False
            else:
                self.sleep_next_fifteen_min()

    def get_candledata_indicator(self):
        ema_small = EMA(interval=23, on='close')
        ema_large = EMA(interval=53, on='close')
        rsi_14 = None #RSI(on='close')
        data = self.market_data.get_candle_data(interval=interval_enum.FIFTEEN_MINUTE, candles=60,
                                                share_symbol='3273', exchange='NSE')
        data = ema_small.cal_indicator(data=data)
        data = ema_large.cal_indicator(data=data)
        data = rsi_14.cal_indicator(data=data)
        return data

    def generateTrade(self, client, direction, stoploss):
        ltp = self.market_data.get_market_data(self.token_detail.token)
        if direction == Direction.BUY:
            if math.floor((ltp - stoploss) / 0.0025) > 15:
                return
            opposite_dir = Direction.SELL
        else:
            if math.floor((stoploss - ltp) / 0.0025) > 15:
                return
            opposite_dir = Direction.BUY
        trade = Trade(tradingSymbol=self.token_detail.symbol, symbolToken=self.token_detail.token, clientId=client,
                      strategy_trade_id=self.client_list.get(client))
        trade.strategy = self.__class__.__name__
        trade.instrument_type = Segment.CURRENCY
        trade.create_trade_orderType_market(direction, self.quantity, Duration.DAY, self.productType, stoploss)
        orderId = self.placeTrade(trade, client)
        # placing Stoploss
        # sl_system_id = self.placeStoploss(trade.system_tradeID, opposite_dir, client, stop_loss)
        fill_price = 0
        while True:
            trade_model = TradeManager.get_trade(self.__class__.__name__, trade.system_tradeID)
            if not trade_model:
                continue
            if trade_model.order_status == OrderStatus.COMPLETE:
                fill_price = trade_model.price
                break
        target = fill_price + (math.floor(abs(fill_price - stoploss) / 0.0025) * 1.5) * 0.0025
        sell_system_id = ''
        while True:
            latest_ltp = self.market_data.get_market_data(self.token_detail.token)
            sell_trade = False
            if latest_ltp >= target:
                sell_trade = True
            elif latest_ltp <= stoploss:
                sell_trade = True
            elif datetime.now() > self.squareOffTimestamp:
                sell_trade = True
            if sell_trade:
                trade = Trade(tradingSymbol=self.token_detail.symbol, symbolToken=self.token_detail.token,
                              clientId=client,
                              strategy_trade_id=self.client_list.get(client))
                trade.strategy = self.__class__.__name__
                trade.instrument_type = Segment.CURRENCY
                trade.create_trade_orderType_market(opposite_dir, self.quantity, Duration.DAY, self.productType,
                                                    stoploss)
                orderId = self.placeTrade(trade, client)
                sell_system_id = trade.system_tradeID
                break
            time.sleep(1)

        while True:
            trade_model = TradeManager.get_trade(self.__class__.__name__, sell_system_id)
            if not trade_model:
                continue
            if trade_model.order_status == OrderStatus.COMPLETE:
                self.emptyTradedf(client)
                break

    def placeStoploss(self, previous_system_id, direction, client, stoploss):
        while True:
            trade_model = TradeManager.get_trade(self.__class__.__name__, previous_system_id)
            if not trade_model:
                continue
            if trade_model.order_status == OrderStatus.COMPLETE:
                trade = Trade(tradingSymbol=self.token_detail.symbol, symbolToken=self.token_detail.token,
                              clientId=client,
                              strategy_trade_id=self.client_list.get(client))
                trade.strategy = self.__class__.__name__
                trade.instrument_type = Segment.CURRENCY
                trade.create_trade_orderType_stoploss_market(direction, self.quantity, stoploss, Duration.DAY,
                                                             self.productType)
                self.placeTrade(trade, client)
                break
        return trade.system_tradeID

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
            return self.trade_manager.addNewTrade(trade)
        else:
            return self.trade_manager.incubate_trade(trade)

    def emptyTradedf(self, client):
        trade_df = self.trade_dataframe.loc[client]
        trade_df['buy_trade'] = 0
        trade_df['sell_trade'] = 0

    def sleep_next_fifteen_min(self):
        now = datetime.now()
        newtime = now.replace(minute=int(now.minute / 15) * 15, second=0, microsecond=0) + timedelta(minutes=15)
        waitSeconds = Utils.getEpoch(newtime) - Utils.getEpoch(now)
        if waitSeconds > 0:
            time.sleep(waitSeconds)

    def sleep_next_five_min(self):
        now = datetime.now()
        newtime = now.replace(minute=int(now.minute / 5) * 5, second=0, microsecond=0) + timedelta(minutes=5)
        waitSeconds = Utils.getEpoch(newtime) - Utils.getEpoch(now)
        if waitSeconds > 0:
            time.sleep(waitSeconds)
