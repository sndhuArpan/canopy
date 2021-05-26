import logging
import uuid

from src.models.OrderType import OrderType
from src.models.ProductType import ProductType
from src.models.TradeState import TradeState
from src.models.Variety import Variety

from utils.Utils import Utils


class Trade:
    def __init__(self, tradingSymbol=None,clientId=None,strategy_trade_id=None):
        self.exchange = "NSE"
        self.system_tradeID = uuid.uuid4()  # Unique ID for each trade
        self.strategy_trade_id = strategy_trade_id
        self.tradingSymbol = tradingSymbol
        self.clientId = clientId
        self.strategy = ""
        self.direction = ""
        self.duration = ""
        self.variety = ''
        self.orderType = ''
        self.productType = ProductType.MIS
        self.instrument_type = ''
        self.intradaySquareOffTimestamp = None  # Can be strategy specific. Some can square off at 15:00:00 some can at 15:15:00 etc.
        self.requestedEntry = 0  # Requested entry
        self.entry = 0  # Actual entry. This will be different from requestedEntry if the order placed is Market order
        self.qty = 0  # Requested quantity
        self.filledQty = 0  # In case partial fill qty is not equal to filled quantity
        self.initialStopLoss = 0  # Initial stop loss
        self.stopLoss = 0
        self.stopLoss_trigger_price = 0
        self.target = 0  # Target price if applicable
        self.cmp = 0  # Last traded price

        self.tradeState = TradeState.CREATED  # state of the trade
        self.timestamp = None  # Set this timestamp to strategy timestamp if you are not sure what to set
        self.createTimestamp = Utils.getEpoch()  # Timestamp when the trade is created (Not triggered)
        self.startTimestamp = None  # Timestamp when the trade gets triggered and order placed
        self.endTimestamp = None  # Timestamp when the trade ended
        self.pnl = 0  # Profit loss of the trade. If trade is Active this shows the unrealized pnl else realized pnl
        self.pnlPercentage = 0  # Profit Loss in percentage terms
        self.exit = 0  # Exit price of the trade
        self.exitReason = None  # SL/Target/SquareOff/Any Other

        self.entryOrder = None  # Object of Type ordermgmt.Order
        self.slOrder = None  # Object of Type ordermgmt.Order
        self.targetOrder = None  # Object of Type ordermgmt.Order

    def equals(self, trade):  # compares to trade objects and returns True if equals
        if trade == None:
            return False
        if self.system_tradeID == trade.system_tradeID:
            return True
        if self.tradingSymbol != trade.tradingSymbol:
            return False
        if self.strategy != trade.strategy:
            return False
        if self.direction != trade.direction:
            return False
        if self.productType != trade.productType:
            return False
        if self.requestedEntry != trade.requestedEntry:
            return False
        if self.qty != trade.qty:
            return False
        if self.timestamp != trade.timestamp:
            return False
        return True

    def create_trade_orderType_market(self, direction, quantity, duration, productType, stoploss):
        self.orderType = OrderType.MARKET
        self.direction = direction
        self.qty = quantity
        self.stopLoss = stoploss
        self.duration = duration
        self.productType = productType
        self.variety = Variety.NORMAL

    def create_trade_orderType_limit(self, direction, quantity, entry_price, duration, productType, stoploss):
        self.orderType = OrderType.LIMIT
        self.direction = direction
        self.qty = quantity
        self.stopLoss = stoploss
        self.duration = duration
        self.productType = productType
        self.requestedEntry = entry_price
        self.variety = Variety.NORMAL

    def create_trade_orderType_stoploss(self, direction, quantity, trigger_price, stoploss, duration, productType):
        self.orderType = OrderType.SL_LIMIT
        self.direction = direction
        self.qty = quantity
        self.duration = duration
        self.productType = productType
        self.stopLoss_trigger_price = trigger_price
        self.stopLoss = stoploss
        self.variety = Variety.STOPLOSS

    def create_trade_orderType_stoploss_market(self, direction, quantity, trigger_price, duration, productType):
        self.orderType = OrderType.SL_MARKET
        self.direction = direction
        self.qty = quantity
        self.duration = duration
        self.productType = productType
        self.stopLoss_trigger_price = trigger_price
        self.variety = Variety.STOPLOSS

    def __str__(self):
        return "ID=" + str(self.system_tradeID) + ", state=" + self.tradeState + ", symbol=" + self.tradingSymbol \
               + ", strategy=" + self.strategy + ", direction=" + self.direction \
               + ", productType=" + self.productType + ", reqEntry=" + str(self.requestedEntry) \
               + ", stopLoss=" + str(self.stopLoss) + ", target=" + str(self.target) \
               + ", entry=" + str(self.entry) + ", exit=" + str(self.exit) \
               + ", profitLoss" + str(self.pnl)
