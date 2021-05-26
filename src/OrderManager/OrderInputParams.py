from src.models.Segment import Segment
from src.models.ProductType import ProductType


class OrderInputParams:
    def __init__(self, tradingSymbol=None, symbolToken=None, trade=None):
        self.exchange = "NSE"  # default
        if trade is None:
            self.variety = ''  # variety
            self.orderId = ''
            self.direction = ''
            self.productType = ''  # Product type (CNC,MIS)t
            self.tradingSymbol = ''  # Trading Symbol of the instrument
            self.symbolToken = ''  # Symbol Token is unique identifier
            self.duration = ''  # Order duration (DAY,IOC)
            self.orderType = ''  # Order type (MARKET, LIMIT etc.)
            self.qty = ''
            self.price = ''  # The min or max price to execute the order at (for LIMIT orders)
            self.triggerPrice = ''  # The price at which an order should be triggered (SL, SL-M)
            self.squareoff = ''  # Only For ROBO (Bracket Order)
            self.stoploss = ''  # Only For ROBO (Bracket Order)
            self.trailingStopLoss = ''  # Only For ROBO (Bracket Order)
            self.disclosedquantity = ''  # Quantity to disclose publicly (for equity trades)
            self.ordertag = ''
            return
        self.variety = trade.variety  # variety
        self.orderId = ''
        self.direction = trade.direction
        self.productType = trade.productType  # Product type (CNC,MIS)t
        self.tradingSymbol = tradingSymbol # Trading Symbol of the instrument
        self.symbolToken = symbolToken # Symbol Token is unique identifier
        self.duration = trade.duration #Order duration (DAY,IOC)
        self.orderType = trade.orderType  # Order type (MARKET, LIMIT etc.)
        self.qty = trade.qty
        self.price = trade.requestedEntry # The min or max price to execute the order at (for LIMIT orders)
        self.triggerPrice = trade.stopLoss_trigger_price  # The price at which an order should be triggered (SL, SL-M)
        self.squareoff = 0 #Only For ROBO (Bracket Order)
        self.stoploss = trade.stopLoss  # Only For ROBO (Bracket Order)
        self.trailingStopLoss = ''# Only For ROBO (Bracket Order)
        self.disclosedquantity = '' # Quantity to disclose publicly (for equity trades)
        self.ordertag = trade.system_tradeID  #It is optional to apply to an order to identify.

    def __str__(self):
        return "symbol=" + str(self.tradingSymbol) + ", symbolToken=" + str(
            self.symbolToken) + ", exchange=" + self.exchange \
               + ", productType=" + self.productType + ", segment=" + self.segment \
               +  ", orderType=" + self.orderType \
               + ", qty=" + str(self.qty) + ", price=" + str(self.price) + ", triggerPrice=" + str(self.triggerPrice) \
               + ", isFnO=" + str(self.isFnO)
