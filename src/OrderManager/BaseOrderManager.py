from smartapi import SmartConnect
from src.DB.static_db.BrokerAppDetails import BrokerAppDetails


class BaseOrderManager:
  def __init__(self, broker, clientId):
    self.broker = broker
    self.clientId = clientId
    self.brokerHandle = BrokerAppDetails().get_normal_connection(self.clientId)

  def placeOrder(self, orderInputParams):
    pass

  def modifyOrder(self, order, orderModifyParams):
    pass

  def modifyOrderToMarket(self, order):
    pass

  def cancelOrder(self, order):
    pass

  def fetchAndUpdateAllOrderDetails(self, orders):
    pass

  def convertToBrokerProductType(self, productType):
    return productType

  def convertToBrokerOrderType(self, orderType):
    return orderType

  def convertToBrokerDirection(self, direction):
    return direction