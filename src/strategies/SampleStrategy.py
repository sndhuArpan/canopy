import json
import logging
import os
import uuid

from Data_Wrappers.Indicators.EMA import EMA
from src.models.Duration import Duration
from src.models.OrderStatus import OrderStatus
from src.models.OrderType import OrderType
from src.models.ProductType import ProductType
from src.models.Direction import Direction
from src.models.Exchange import Exchange
from src.models.Segment import Segment
from src.strategies.BaseStrategy import BaseStrategy
from src.trademanager.Trade import Trade
from src.trademanager.TradeManager import TradeManager
from utils.Utils import Utils, interval_enum
from datetime import timedelta, datetime
import time
import threading


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
        self.symbols = ["TCS-EQ", "MARUTI-EQ", "BRITANNIA-EQ", "RELIANCE-EQ", "HDFCBANK-EQ", "CIPLA-EQ"]
        self.slPercentage = 1.1
        self.targetPerncetage = 2.2
        self.startTimestamp = Utils.getTimeOfToDay(10, 1, 0)  # When to start the strategy. Default is Market start time
        self.stopTimestamp = Utils.getTimeOfToDay(13, 10,
                                                  0)  # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.squareOffTimestamp = Utils.getTimeOfToDay(15, 0, 0)  # Square off time
        self.capital = 3000  # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.leverage = 2  # 2x, 3x Etc
        self.maxTradesPerDay = 1  # Max number of trades per day under this strategy
        self.isFnO = True  # Does this strategy trade in FnO or not
        self.capitalPerSet = 0  # Applicable if isFnO is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
        self.valid_dict = {}
        self.watch_share = {}
        self.symbol_token_dict = {}
        self.placed_trades = []
        self.client_list = {}
        tFile = open(os.path.abspath('src/data/client_strategy_map.py'), 'r')
        client_strategy_data = json.loads(tFile.read())['mapping']
        for i in client_strategy_data:
            if self.__class__.__name__ == i['strategy']:
                for client in i['client']:
                    self.client_list[client] = uuid.uuid1()

    def process(self):
        # for share in self.symbols:
        #     print(share)
        #     print(datetime.now())
        #     token = self.getQuote(share, self.exchange)
        #     self.symbol_token_dict[token] = share
        #     data = self.angel_data.get_candle_data(share_symbol=token, interval=interval_enum.FIFTEEN_MINUTE)
        #     high_range = data['high'][0]
        #     low_range = data['low'][0]
        #     valid_count = 0
        #     out = 0
        #     for i in range(2):
        #         idx = 1 + i
        #         if data['open'][idx] <= high_range and data['close'][idx] <= high_range:
        #             if data['open'][idx] >= low_range and data['close'][idx] >= low_range:
        #                 valid_count = valid_count + 1
        #                 if data['high'][idx] > high_range or data['low'][idx] < low_range:
        #                     out = out + 1
        #     if valid_count == 2 and out <= 1:
        #         self.valid_dict[token] = {'high_range': high_range, 'low_range': low_range, 'out': out}
        # print(self.symbol_token_dict)
        # print(self.valid_dict)
        # next_candle_time = Utils.getTimeOfToDay(10, 15, 0)
        # now = datetime.now()
        # if now < next_candle_time:
        #     waitSeconds = Utils.getEpoch(next_candle_time) - Utils.getEpoch(now)
        #     if waitSeconds > 0:
        #         time.sleep(waitSeconds)
        # print('scan for watch share start')
        # for x in self.valid_dict:
        #     dict_data = self.valid_dict.get(x)
        #     data = self.angel_data.get_candle_data(share_symbol=x, interval=interval_enum.FIFTEEN_MINUTE)
        #     last_index = 3
        #     high_range = dict_data.get('high_range')
        #     low_range = dict_data.get('low_range')
        #     out = dict_data.get('out')
        #     valid_count = 0
        #     if data['open'][last_index] <= high_range and data['close'][last_index] <= high_range:
        #         if data['open'][last_index] >= low_range and data['close'][last_index] >= low_range:
        #             valid_count = valid_count + 1
        #             if data['high'][last_index] > high_range or data['low'][last_index] < low_range:
        #                 out = out + 1
        #     if valid_count == 1 and out <= 1:
        #         margin_high_range = high_range - (high_range * 0.15) / 100
        #
        #         margin_low_range = low_range + (low_range * 0.15) / 100
        #         cmp_high_range = high_range - (high_range * 0.02) / 100
        #
        #         cmp_low_range = low_range + (low_range * 0.02) / 100
        #         self.watch_share[x] = {'high_range': high_range, 'low_range': low_range,
        #                                    'margin_high_range': margin_high_range, 'margin_low_range': margin_low_range,
        #                                    'cmp_high_range': cmp_high_range, 'cmp_low_range': cmp_low_range}
        # print(self.watch_share)
        # self.watch_trades()

        self.generateTrade('IDEA-EQ', Direction.BUY)

    def watch_trades(self):
        ema = EMA(interval=23, on='close')
        ema_name = 'ema_23'
        day_start = Utils.get_hour_start_date(datetime.today(), interval_enum.FIFTEEN_MINUTE).strftime(
            "%Y-%m-%dT%H:%M:%S+05:30")
        in_trade = False
        while True:
            if not self.watch_share:
                break
            for x in self.watch_share:
                share_dict = self.watch_share.get(x)
                cmp = self.get_ltp(x)
                if cmp >= share_dict.get('cmp_high_range'):
                    data = self.angel_data.get_candle_data(share_symbol=x, candles=50,
                                                           interval=interval_enum.FIFTEEN_MINUTE)
                    data = ema.cal_indicator(data=data)
                    last_index = data.index[-1]
                    day_start_index = data.index[data['datetime'] == day_start].tolist()[0]
                    if data['close'][last_index] > data[ema_name][last_index] > data[ema_name][day_start_index]:
                        cmp = self.get_ltp(x)
                        if cmp >= share_dict.get('high_range'):
                            print('generate buy order for ' + self.symbol_token_dict.get(x) + ' at price ' + str(cmp))
                            in_trade = True
                            break
                if cmp <= share_dict.get('cmp_low_range'):
                    data = self.angel_data.get_candle_data(share_symbol=x, candles=50,
                                                           interval=interval_enum.FIFTEEN_MINUTE)
                    data = ema.cal_indicator(data=data)
                    last_index = data.index[-1]
                    day_start_index = data.index[data['datetime'] == day_start].tolist()[0]
                    if data['close'][last_index] < data[ema_name][last_index] < data[ema_name][day_start_index]:
                        cmp = self.get_ltp(x)
                        if cmp >= share_dict.get('cmp_low_range'):
                            print('generate sell order for ' + self.symbol_token_dict.get(x) + ' at price ' + str(cmp))
                            in_trade = True
                            break
            now = datetime.now()

            if now > self.stopTimestamp or in_trade:
                break

    def get_ltp(self, token):
        data_dict = self.angel_data.connect.ltpData('NSE', self.symbol_token_dict.get(token), str(token)).__getitem__(
            'data')
        return data_dict.__getitem__('ltp')

    def generateTrade(self, tradingSymbol, direction):
        buy_system_trade_id = ''
        sl_1_trade_id = '51fa98fa-0697-454e-a55d-0bd960f620fb'
        sl_2_trade_id = '89a283c1-acdf-453a-ab80-952e1de353d2'
        for client_key in self.client_list:
            trade = Trade(tradingSymbol=tradingSymbol, clientId=client_key, strategy_trade_id=self.client_list.get(client_key))
            trade.strategy = self.__class__.__name__
            trade.instrument_type = Segment.EQUITY
            stoploss = 8.45
            trade.create_trade_orderType_market(direction, 2, Duration.DAY, self.productType, stoploss)
            # Hand over the trade to TradeManager
            buy_system_trade_id = trade.system_tradeID
            t = threading.Thread(target=TradeManager.addNewTrade, args=(trade,), daemon=True)
            t.start()
            print('trade placed')
            self.placed_trades.append(trade.system_tradeID)

        while True:
            trade_model = TradeManager.get_trade(self.__class__.__name__,buy_system_trade_id)
            if not trade_model:
                continue
            if trade_model.order_status == OrderStatus.COMPLETE:
                for client_key in self.client_list:
                    trade = Trade(tradingSymbol=tradingSymbol, clientId=client_key,
                                  strategy_trade_id=self.client_list.get(client_key))
                    trade.strategy = self.__class__.__name__
                    trade.instrument_type = Segment.EQUITY
                    sl_1_trade_id = trade.system_tradeID
                    trade.create_trade_orderType_stoploss(Direction.SELL, 1,8.50,8.45, Duration.DAY, self.productType)
                    # Hand over the trade to TradeManager
                    t = threading.Thread(target=TradeManager.addNewTrade, args=(trade,), daemon=True)
                    t.start()

                    trade = Trade(tradingSymbol=tradingSymbol, clientId=client_key,
                                  strategy_trade_id=self.client_list.get(client_key))
                    trade.strategy = self.__class__.__name__
                    trade.instrument_type = Segment.EQUITY
                    sl_2_trade_id = trade.system_tradeID
                    trade.create_trade_orderType_stoploss_market(Direction.SELL, 1, 8.2, Duration.DAY, self.productType)
                    # Hand over the trade to TradeManager
                    t = threading.Thread(target=TradeManager.addNewTrade, args=(trade,), daemon=True)
                    t.start()
                break

        now = datetime.now()
        if now < self.stopTimestamp:
            waitSeconds = Utils.getEpoch(self.stopTimestamp) - Utils.getEpoch(now)
            logging.info("%s: Waiting for %d seconds till startegy start timestamp reaches...", self.getName(),
                         waitSeconds)
            if waitSeconds > 0:
                time.sleep(waitSeconds)

        trade_model_sl_1 = TradeManager.get_trade(self.__class__.__name__, sl_1_trade_id)
        trade_model_sl_2 = TradeManager.get_trade(self.__class__.__name__, sl_2_trade_id)
        sell_call = False
        qty = 0
        if trade_model_sl_1.order_status != OrderStatus.COMPLETE:
            sell_call = True
            qty = qty +1
            TradeManager.executeCancelTrade(trade_model_sl_1)
        if trade_model_sl_2.order_status not in (OrderStatus.COMPLETE):
            sell_call = True
            qty = qty +1
            TradeManager.executeCancelTrade(trade_model_sl_2)
        sell_trade_id = ''
        if sell_call:
            for client_key in self.client_list:
                trade = Trade(tradingSymbol=tradingSymbol, clientId=client_key,
                              strategy_trade_id=self.client_list.get(client_key))
                trade.strategy = self.__class__.__name__
                trade.instrument_type = Segment.EQUITY
                stoploss = 8.45
                trade.create_trade_orderType_market(Direction.SELL, 1, Duration.DAY, self.productType, stoploss)
                # Hand over the trade to TradeManager
                sell_trade_id = trade.system_tradeID
                t = threading.Thread(target=TradeManager.addNewTrade, args=(trade,), daemon=True)
                t.start()

        while True:
            trade_model = TradeManager.get_trade(self.__class__.__name__, sell_trade_id)
            if not trade_model:
                continue
            if trade_model.order_status == OrderStatus.COMPLETE:
                break


    def shouldPlaceTrade(self, trade, tick):
        # First call base class implementation and if it returns True then only proceed
        if super().shouldPlaceTrade(trade, tick) == False:
            return False

        if tick == None:
            return False

        if trade.direction == Direction.LONG and tick.lastTradedPrice > trade.requestedEntry:
            return True
        elif trade.direction == Direction.SHORT and tick.lastTradedPrice < trade.requestedEntry:
            return True
        return False
