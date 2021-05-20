from smartapi import SmartConnect
from smartapi import WebSocket
from time import sleep
from src.ticker.BaseTicker import BaseTicker
from src.ticker.AngelSymbol.AngelSymbol import AngelSymbol
from src.models.TickData import TickData


class AngelTicker(BaseTicker):

    def __init__(self, login_nickname, logger):
        super(AngelTicker, self).__init__(login_nickname, logger)
        self.ticker = None

    def startTicker(self):
        self.connect = SmartConnect(api_key=self.broker_detail_obj.web_socket_api_key)
        self.connect.generateSession(self.broker_detail_obj.client_id,
                                     self.broker_detail_obj.password)
        feedToken = self.connect.getfeedToken()
        self.ticker = WebSocket(feedToken, self.broker_detail_obj.client_id)

        self.ticker.on_connect = self.on_connect
        self.ticker.on_close = self.on_close
        self.ticker.on_error = self.on_error
        self.ticker.on_reconnect = self.on_reconnect
        self.ticker.on_noreconnect = self.on_noreconnect
        self.ticker.on_ticks = self.on_ticks
        self.ticker.on_order_update = self.on_order_update

        self.logger.info('Ticker: Going to connect..')
        self.ticker.connect(threaded=True)
        while not self.ticker.is_connected():
            sleep(1)
            print('Waiting to connect')


    def stopTicker(self):
        self.logger.info('Ticker: stopping..')
        self.ticker.close(1000, "Manual close")

    def registerSymbols(self, symbols):
        for symbol in symbols:
            #isd = None #Instruments.getInstrumentDataBySymbol(symbol)
            #token = isd['instrument_token']
            #symbol = 'nse_cm|' + symbol
            self.logger.info('Ticker registerSymbol: %s token = %s', symbol)
            self.ticker.websocket_connection()
            dict = {'token': symbol, 'task': 'mw'}
            self.ticker.send_request(**dict)

        self.logger.info('Ticker Subscribing tokens %s', symbols)
        #self.ticker.subscribe(tokens)

    def unregisterSymbols(self, symbols):
        tokens = []
        for symbol in symbols:
            isd = None #Instruments.getInstrumentDataBySymbol(symbol)
            token = isd['instrument_token']
            self.logger.info('Ticker unregisterSymbols: %s token = %s', symbol, token)
            tokens.append(token)

        self.logger.info('Ticker Unsubscribing tokens %s', tokens)
        #self.ticker.unsubscribe(tokens)

    def on_ticks(self, ws, brokerTicks):
        # convert broker specific Ticks to our system specific Ticks (models.TickData) and pass to super class function
        ticks = []
        for bTick in brokerTicks:
            print(bTick)
            break
            #isd = Instruments.getInstrumentDataByToken(bTick['instrument_token'])
        #     tradingSymbol = AngelSymbol.get_symbol_token('MCX', bTick['tk'])
        #     tick = TickData(tradingSymbol)
        #     tick.lastTradedPrice = bTick['last_price']
        #     tick.lastTradedQuantity = bTick['last_quantity']
        #     tick.avgTradedPrice = bTick['average_price']
        #     tick.volume = bTick['volume']
        #     tick.totalBuyQuantity = bTick['buy_quantity']
        #     tick.totalSellQuantity = bTick['sell_quantity']
        #     tick.open = bTick['ohlc']['open']
        #     tick.high = bTick['ohlc']['high']
        #     tick.low = bTick['ohlc']['low']
        #     tick.close = bTick['ohlc']['close']
        #     tick.change = bTick['change']
        #     ticks.append(tick)
        #
        # self.onNewTicks(ticks)

    def on_connect(self, ws, response):
        self.onConnect()

    def on_close(self, ws, code, reason):
        self.onDisconnect(code, reason)

    def on_error(self, ws, code, reason):
        self.onError(code, reason)

    def on_reconnect(self, ws, attemptsCount):
        self.onReconnect(attemptsCount)

    def on_noreconnect(self, ws):
        self.onMaxReconnectsAttempt()

    def on_order_update(self, ws, data):
        self.onOrderUpdate(data)


if __name__ == '__main__':
    from Logging.Logger import GetLogger
    import time
    logger = GetLogger().get_logger()


    def tickerListener(tick):
        logger.info('tickerLister: onNewTick %s', vars(tick))

    ticker = AngelTicker('BHUPI_ANGEL', logger)
    ticker.startTicker()
    ticker.registerListener(tickerListener)
    ticker.registerSymbols(['nse_cm|2885'])
    # wait for 10 seconds and stop ticker service
    time.sleep(10)
    logger.info('Going to stop ticker')
    ticker.stopTicker()

    # obj = AngelTicker('BHUPI_ANGEL', logger)
    # obj.startTicker()
    # obj.registerSymbols(['mcx_fo|224395'])
    # obj.on_ticks
    # #obj.stopTicker()

    # _req = '{"task":"cn","channel":"","token":"' + FEED_TOKEN + '","user": "' + CLIENT_CODE + '","acctid":"' + CLIENT_CODE + '"}';
    #
    # websocketObj.send(_req)
    #
    #
    #
    # strwatchlistscrips = "nse_cm|2885&nse_cm|1594&nse_cm|11536";
    #
    # _req = '{"task":"mw","channel":"' + strwatchlistscrips + '","token":"' + FEED_TOKEN + '","user": "' + CLIENT_CODE + '","acctid":"' + CLIENT_CODE + '"}';
    #
    # websocketObj.send(_req);