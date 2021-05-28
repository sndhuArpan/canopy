from src.models.BrokerAppDetails import BrokerAppDetails


class BaseTicker:

  def __init__(self, client_id, logger):
    self.broker_detail_obj = BrokerAppDetails.get_connection_details(client_id)
    self.logger = logger
    self.ticker = None
    self.tickListeners = []

  def startTicker(self):
    pass

  def stopTicker(self):
    pass

  def registerListener(self, listener):
    # All registered tick listeners will be notified on new ticks
    self.tickListeners.append(listener)

  def registerSymbols(self, exchange, token):
    pass

  def unregisterSymbols(self, exchange, token):
    pass

  def onNewTicks(self, ticks):
    # logging.info('New ticks received %s', ticks)
    for tick in ticks:
      for listener in self.tickListeners:
        try:
          listener(tick)
        except Exception as e:
          self.logger.error('BaseTicker: Exception from listener callback function. Error => %s', str(e))

  def onConnect(self):
    self.logger.info('Ticker connection successful.')

  def onDisconnect(self, code, reason):
    self.logger.error('Ticker got disconnected. code = %d, reason = %s', code, reason)

  def onError(self, code, reason):
    self.logger.error('Ticker errored out. code = %d, reason = %s', code, reason)

  def onReconnect(self, attemptsCount):
    self.logger.warn('Ticker reconnecting.. attemptsCount = %d', attemptsCount)

  def onMaxReconnectsAttempt(self):
    self.logger.error('Ticker max auto reconnects attempted and giving up..')

  def onOrderUpdate(self, data):
    #logging.info('Ticker: order update %s', data)
    pass
