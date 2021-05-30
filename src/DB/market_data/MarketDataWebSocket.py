from smartapi import WebSocket
from smartapi import SmartConnect
from src.DB.market_data.Market_Data import TickerMsg
from src.DB.static_db.BrokerAppDetails import BrokerAppDetails


class MarketDataWebsocket:

    def __init__(self, client_id, logger):
        self.logger = logger
        self.client_id = client_id
        self.connection_detail = BrokerAppDetails().get_brokerclientdetails(client_id)
        self.token = None
        self.task = "mw"

    def start_ticker(self):
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


if __name__ == '__main__':
    from Logging.Logger import GetLogger
    from Market_Data import LtpPriceModel, MarketData
    # token1 = LtpPriceModel()
    # token1.initialze('9059', 'MCX')
    # token2 = LtpPriceModel()
    # token2.initialze('228530', 'MCX')
    # token3 = LtpPriceModel()
    # token3.initialze('220822', 'MCX')
    # MarketData_obj = MarketData()
    # MarketData_obj.register_token(token1)
    # MarketData_obj = MarketData()
    # MarketData_obj.register_token(token2)
    # MarketData_obj = MarketData()
    # MarketData_obj.register_token(token3)
    logger = GetLogger().get_logger()
    obj = MarketDataWebsocket('S705342', logger)
    try:
        obj.start_ticker()
    except Exception as e:
        print('Out of start')