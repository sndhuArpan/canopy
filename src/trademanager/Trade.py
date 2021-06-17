import logging
import uuid

from src.models.OrderType import OrderType
from src.models.ProductType import ProductType
from src.models.TradeState import TradeState
from src.models.Variety import Variety


class Trade:
    def __init__(self, tradingSymbol=None, symbolToken=None, clientId=None, strategy_trade_id=None):
        self.exchange = 'NSE'
        self.system_tradeID = uuid.uuid4()  # Unique ID for each trade
        self.strategy_trade_id = strategy_trade_id
        self.tradingSymbol = tradingSymbol
        self.symbolToken = symbolToken
        self.clientId = clientId
        self.strategy = ""
        self.direction = ""
        self.duration = ""
        self.variety = ''
        self.orderType = ''
        self.productType = ProductType.MIS
        self.instrument_type = ''
        self.requestedEntry = 0  # Requested entry
        self.qty = 0  # Requested quantity
        self.stop_loss = 0
        self.tradeState = TradeState.CREATED
        self.stopLoss_trigger_price = 0

    def create_trade_orderType_market(self, direction, quantity, duration, productType, stoploss):
        self.orderType = OrderType.MARKET
        self.direction = direction
        self.qty = quantity
        self.stop_loss = stoploss
        self.duration = duration
        self.productType = productType
        self.variety = Variety.NORMAL

    def create_trade_orderType_limit(self, direction, quantity, entry_price, duration, productType, stoploss):
        self.orderType = OrderType.LIMIT
        self.direction = direction
        self.qty = quantity
        self.stop_loss = stoploss
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
        self.stop_loss = stoploss
        self.variety = Variety.STOPLOSS

    def create_trade_orderType_stoploss_market(self, direction, quantity, trigger_price, duration, productType):
        self.orderType = OrderType.SL_MARKET
        self.direction = direction
        self.qty = quantity
        self.duration = duration
        self.productType = productType
        self.stopLoss_trigger_price = trigger_price
        self.variety = Variety.STOPLOSS
