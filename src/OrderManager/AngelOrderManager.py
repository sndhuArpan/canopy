import logging
from src.OrderManager.BaseOrderManager import BaseOrderManager
from src.OrderManager.Order import Order
from src.models.Angel.TransactionType import TransactionType
from src.models.Direction import Direction
from src.models.OrderType import OrderType
from src.models.Angel.OrderType import OrderType as angel_order_type
from src.models.ProductType import ProductType
from src.models.Angel.ProductType import ProductType as angel_product_type
from utils.Utils import Utils


class AngelOrderManager(BaseOrderManager):
    def __init__(self,broker,clientId):
        super().__init__(broker,clientId)

    def placeOrder(self, orderInputParams):
        logging.info('%s: Going to place order with params %s', self.broker, orderInputParams)
        angel_connect = self.brokerHandle
        try:
            orderParam = {
                'variety': orderInputParams.variety,
                'tradingsymbol': orderInputParams.tradingSymbol,
                'symboltoken': orderInputParams.symbolToken,
                'transactiontype': self.convertToBrokerTransactionType(orderInputParams.direction),
                'exchange': orderInputParams.exchange,
                'ordertype': self.convertToBrokerOrderType(orderInputParams.orderType),
                'producttype': self.convertToBrokerProductType(orderInputParams.productType),
                'duration': orderInputParams.duration,
                'price': str(orderInputParams.price),
                'quantity': str(orderInputParams.qty),
                'triggerprice': str(orderInputParams.triggerPrice),
                'squareoff': str(orderInputParams.squareoff),
                'stoploss': str(orderInputParams.stoploss),
                'trailingStopLoss': str(orderInputParams.trailingStopLoss),
                'disclosedquantity': str(orderInputParams.disclosedquantity),
                'ordertag': str(orderInputParams.ordertag)
            }

            orderId = angel_connect.placeOrder(orderParam)

            logging.info('%s: Order placed successfully, orderId = %s', self.broker, orderId)
            order = Order(orderInputParams)
            order.orderId = orderId
            order.orderPlaceTimestamp = Utils.getEpoch()
            order.lastOrderUpdateTimestamp = Utils.getEpoch()
            return order
        except Exception as e:
            logging.info('%s Order placement failed: %s', self.broker, str(e))
            raise Exception(str(e))

    def get_tradeBook(self):
        return self.brokerHandle.tradeBook().__getitem__('data')

    def convertToBrokerProductType(self, productType):
        if productType == ProductType.MIS:
            return angel_product_type.MARGIN
        elif productType == ProductType.NRML:
            return angel_product_type.INTRADAY
        elif productType == ProductType.CNC:
            return angel_product_type.DELIVERY
        return None

    def convertToBrokerTransactionType(self, direction):
        if direction == Direction.LONG:
            return TransactionType.BUY
        elif direction == Direction.SHORT:
            return TransactionType.SELL
        return None

    def convertToBrokerOrderType(self, orderType):
        if orderType == OrderType.LIMIT:
            return angel_order_type.LIMIT
        elif orderType == OrderType.MARKET:
            return angel_order_type.MARKET
        elif orderType == OrderType.SL_MARKET:
            return angel_order_type.SL_MARKET
        elif orderType == OrderType.SL_LIMIT:
            return angel_order_type.SL_LIMIT
        return None
