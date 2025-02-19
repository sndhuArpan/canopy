from smartapi.smartConnect import SmartConnect
from smartapi.webSocket import WebSocket

from src.DB.market_data.Market_Data import TickerMsg, MarketData, LtpPriceModel
from src.DB.static_db.BrokerAppDetails import BrokerAppDetails

import warnings
warnings.filterwarnings("ignore")


class MarketDataWebsocket:

    def __init__(self, client_id, logger):
        self.logger = logger
        self.client_id = client_id
        self.connection_detail = BrokerAppDetails().get_brokerclientdetails(client_id)
        self.token = None
        self.task = "mw"
        self.logger.info('MarketDataWebsocket object initiated')

    def start_ticker(self):
        self.logger.info('MarketDataWebsocket: Starting ticker')
        self.market_data_db_obj = MarketData()
        self.token = self.market_data_db_obj.get_register_token_string()
        self.connect = SmartConnect(api_key=self.connection_detail.websocket_api_key)
        self.connect.generateSession(self.client_id, self.connection_detail.password)
        self.feed_token = self.connect.getfeedToken()
        self.ss = WebSocket(self.feed_token, self.client_id)
        self.ss.on_ticks = self.on_tick
        self.ss.on_connect = self.on_connect
        self.ss.on_close = self.on_close
        self.ss.connect()
        raise Exception('Ticker connection lost')

    def on_tick(self, ws, tick):
        token_str = self.market_data_db_obj.get_register_token_string()
        if token_str != self.token:
            self.logger.info('Updating Ticker : %s' % token_str)
            self.token = token_str
            self.ss.send_request(self.token, self.task)
        for bTick in tick:
            if 'ltp' in bTick.keys() and 'v' in bTick.keys():
                token = LtpPriceModel().initialize(bTick['tk'], bTick['e'])
                token.ltp_price = bTick['ltp']
                token.volume = bTick['v']
                token.ltp_time = bTick['ltt']
                self.market_data_db_obj.update_ltp(token)
            if 'msg' in bTick.keys() and 'ak' in bTick.keys():
                status_msg = TickerMsg().initialize(bTick['msg'], bTick['ak'])
                self.market_data_db_obj.insert_into_ticker_message(status_msg)

    def on_connect(self, ws, response):
        ws.websocket_connection()  # Websocket connection
        ws.send_request(self.token, self.task)

    def send_request(self, ws):
        ws.send_request(self.token, self.task)

    def on_close(self, ws, code, reason):
        ws.stop()


# if __name__ == '__main__':
#     from Logging.Logger import GetLogger
#     from Market_Data import LtpPriceModel, MarketData
#     from src.DB.static_db.TickerDetails import TickerDetails
#     token1 = LtpPriceModel()
#     token1.initialize('9059', 'MCX')
#     token_detail = TickerDetails().get_future_token('CDS', 'USDINR')
#     # market db object
#     # Register Symbols
#     ltp_model = LtpPriceModel().initialize(token_detail.token, token_detail.exch_seg)
#     # self.market_data.register_token(ltp_model)
#     MarketData_obj = MarketData()
#     MarketData_obj.register_token(token1)
#     MarketData_obj.register_token(ltp_model)
#     # MarketData_obj = MarketData()
#     # MarketData_obj.register_token(token2)
#     # MarketData_obj = MarketData()
#     # MarketData_obj.register_token(token3)
#     logger = GetLogger().get_logger()
#     obj = MarketDataWebsocket('S705342', logger)
#     try:
#         obj.start_ticker()
#     except Exception as e:
#         print('Out of start')