from smartapi import SmartConnect


class BaseOrderManager:
  def __init__(self, broker, clientId):
    self.broker = broker
    connect = SmartConnect(api_key="RTebKHaN")
    connect.generateSession("S705342", "poiuhbnm@2")
    self.brokerHandle = connect

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