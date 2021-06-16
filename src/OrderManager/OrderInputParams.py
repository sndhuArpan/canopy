from src.models.Segment import Segment
from src.models.ProductType import ProductType


class OrderInputParams:
    def __init__(self, trade=None):
          # default
        if trade is None:
            self.exchange = "NSE"
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
        self.exchange = trade.exchange
        self.variety = trade.variety  # variety
        self.orderId = ''
        self.direction = trade.direction
        self.productType = trade.productType  # Product type (CNC,MIS)t
        self.tradingSymbol = trade.tradingSymbol # Trading Symbol of the instrument
        self.symbolToken = trade.symbolToken # Symbol Token is unique identifier
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
