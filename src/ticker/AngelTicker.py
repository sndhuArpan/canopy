import os
import numpy as np
from smartapi import SmartConnect
from smartapi import WebSocket
from time import sleep
from datetime import datetime, timedelta
#from src.ticker.BaseTicker import BaseTicker
from src.DB.static_db.BrokerAppDetails import BrokerAppDetails
from src.ticker.AngelSymbol.AngelSymbol import AngelSymbol
import pandas as pd


class AngelTicker():

    socket_thread = []

    def __init__(self, client_id, logger):
        #super(AngelTicker, self).__init__(client_id, logger)
        #self.broker_detail_obj = BrokerAppDetails.get_connection_details(client_id)
        self.logger = logger
        self.client_id = client_id
        self.connection_detail = BrokerAppDetails.get_connection_details(self.client_id)
        self.registry_file = os.path.join(os.path.dirname(__file__), 'registerTicker.txt')
        self.data_df = pd.DataFrame(
            columns=['script_token', 'lastTradedTime', 'lastTradedPrice', 'exchange', 'lastTradedQuantity',
                     'totalBuyQuantity',
                     'totalSellQuantity', 'close', 'change', 'volume', 'low'])
        self.connect_status_df = pd.DataFrame( columns= ['time', 'msg', 'status'])
        self.registry_file_mod_time = os.path.getmtime(self.registry_file)
        self.latest_tick_time = None
        self.ticker = None

    def startTicker(self):
        retry = 0
        max_retry = 10
        self.ticker = None
        self.connect = SmartConnect(api_key=self.connection_detail.get('web_socket_api_key'))
        self.connect.generateSession(self.client_id,
                                     self.connection_detail.get('password'))
        self.feedToken = self.connect.getfeedToken()
        self.ticker = WebSocket(self.feedToken, self.client_id, reconnect=False)
        self.ticker.on_connect = self.on_connect
        self.ticker.on_close = self.on_close
        #self.ticker.on_error = self.on_error
        #self.ticker.on_reconnect = self.on_reconnect
        #self.ticker.on_noreconnect = self.on_noreconnect
        self.ticker.on_ticks = self.on_ticks
        #self.ticker.on_order_update = self.on_order_update
        self.logger.info('Ticker: Going to connect..')
        self.ticker.connect(threaded=True)
        while not self.ticker.is_connected():
            print('Waiting to connect, Retry Count %d' % retry)
            retry = retry + 1
            sleep(1)
            if retry == max_retry:
                self.ticker.stop()
                break
        self.loadRegisterSymbols(first_run=True)

    def on_connect(self, ws, response):
        self.logger.info('Ticker connection successful.')
        self.onConnect()

    def stopTicker(self):
        self.logger.info('Ticker: stopping..')
        self.ticker.close(1000, "Manual close")

    def on_close(self, ws, code, reason):
        self.onDisconnect(code, reason)

    def on_error(self, ws, code, reason):
        #print('Func : Ticker on_error : Stop and restart ticker')
        #self.restart_ticker()
        pass

    def on_reconnect(self, ws, attemptsCount):
        # print('Func: on_reconnect : Trying to reconnect')
        # if self.ticker is None:
        #     print('Func : on_reconnect : ERROR Ticker object is None')
        #     print('Func : on_reconnect : Starting websocket again')
        #     self.startTicker()
        # elif not self.ticker.is_connected:
        #     print('Func : on_reconnect : ERROR Ticker object is NOT CONNECTED')
        #     print('Func : on_reconnect : Starting websocket again')
        #     self.startTicker()
        # else:
        #     self.onReconnect(attemptsCount)
        #     self.retry_count = self.retry_count + 1
        pass
        #self.restart_ticker()

    def on_noreconnect(self, ws):
        print('Func : on_noreconnect : If no reconnect, sleeping for 30 sec')
        self.onMaxReconnectsAttempt()

    def on_order_update(self, ws, data):
        self.onOrderUpdate(data)

    def on_ticks(self, ws, brokerTicks):
        self.loadRegisterSymbols()
        for bTick in brokerTicks:
            if 'ltp' in bTick.keys() and 'v' in bTick.keys():
                if bTick['tk'] in self.data_df.script_token.values:
                    self.update_data_df(bTick['tk'], bTick['ltt'], bTick['ltp'], bTick['c'], bTick['lo'],
                                        bTick['ltq'], bTick['bq'], bTick['bs'], bTick['c'], bTick['v'])
                else:
                    self.append_data_df(bTick['tk'], bTick['ltt'], bTick['ltp'], bTick['c'], bTick['lo'], bTick['e'],
                                        bTick['ltq'], bTick['bq'], bTick['bs'], bTick['c'], bTick['v'])
            else:
                if 'msg' in bTick.keys() and 'ak' in bTick.keys():
                    if bTick['msg'] in self.connect_status_df.msg.values:
                        index = self.connect_status_df[self.connect_status_df['msg'] == bTick['msg']].index.values
                        self.connect_status_df.at[index, 'status'] = bTick['ak']
                        self.connect_status_df.at[index, 'time'] = datetime.now()
                    else:
                        dict_cn_st = {'time' : datetime.now(), 'msg' : bTick['msg'], 'status' : bTick['ak']}
                        self.connect_status_df = self.connect_status_df.append(dict_cn_st, ignore_index=True)

    def loadRegisterSymbols(self, first_run = False):
        latest_mod_time = os.path.getmtime(self.registry_file)
        if first_run:
            f = open(self.registry_file, 'r')
            lines = f.readlines()
            symbol_list = '&'.join([line.strip() for line in lines])
            print('Func : loadRegisterSymbols : First time Ticker registerSymbol: %s token' % symbol_list)
            self.ticker.websocket_connection()
            dict = {'token': symbol_list, 'task': 'mw'}
            self.ticker.send_request(**dict)
            print('Func : loadRegisterSymbols : Ticker Subscribing tokens %s' % symbol_list)
            self.registry_file_mod_time = latest_mod_time
        else:
            if latest_mod_time != self.registry_file_mod_time:
                f = open(self.registry_file, 'r')
                lines = f.readlines()
                symbol_list = '&'.join([line.strip() for line in lines])
                print(symbol_list)
                print('Func : loadRegisterSymbols : New Ticker registerSymbol: %s token' % symbol_list)
                self.ticker.websocket_connection()
                dict = {'token': symbol_list, 'task': 'mw'}
                self.ticker.send_request(**dict)
                print('Func : loadRegisterSymbols : Ticker Subscribing tokens %s' % symbol_list)
                self.registry_file_mod_time = latest_mod_time

    def registerSymbols(self, exchange, token):
        print('Func : registerSymbols : Register token to websocket : %s' % token)
        file_object = open(self.registry_file, 'a')
        file_object.write('\n')
        file_object.write(exchange+'|'+str(token))
        # Close the file
        file_object.close()
        if not self.ticker.is_connected:
            self.on_reconnect(self, 2)
        self.loadRegisterSymbols()
        print('Func : registerSymbols : exit' )

    @staticmethod
    def remove_empty_lines(filename):
        if not os.path.isfile(filename):
            print("{} does not exist ".format(filename))
            return
        with open(filename) as filehandle:
            lines = filehandle.readlines()

        with open(filename, 'w') as filehandle:
            lines = filter(lambda x: x.strip(), lines)
            filehandle.writelines(lines)

    def unregisterSymbols(self, exchange, token):
        print('Func : unregisterSymbols : UnRegister token from websocket : %s' % token)
        with open(self.registry_file, "r+") as f:
            d = f.readlines()
            f.seek(0)
            for i in d:
                if i != exchange+'|'+str(token):
                    f.write(i)
            f.truncate()
        AngelTicker.remove_empty_lines(self.registry_file)
        if not self.ticker.is_connected:
            self.on_reconnect(self, 2)
        self.loadRegisterSymbols()
        print('Func : unregisterSymbols : exit' )

    def update_data_df(self, script_token, lastTradedTime, lastTradedPrice, close, low, lastTradedQuantity,
                       totalBuyQuantity ,totalSellQuantity, change, volume) :
        index = self.data_df[self.data_df['script_token'] == script_token].index.values
        self.data_df.at[index, 'lastTradedPrice'] = lastTradedPrice
        self.data_df.at[index, 'lastTradedQuantity'] = lastTradedQuantity
        self.data_df.at[index, 'totalBuyQuantity'] = totalBuyQuantity
        self.data_df.at[index, 'totalSellQuantity'] = totalSellQuantity
        self.data_df.at[index, 'lastTradedTime'] = datetime.strptime(lastTradedTime, '%d/%m/%Y %H:%M:%S')
        self.data_df.at[index, 'close'] = close
        self.data_df.at[index, 'change'] = change
        self.data_df.at[index, 'volume'] = volume
        self.data_df.at[index, 'low'] = low

    def append_data_df(self, script_token, lastTradedTime, lastTradedPrice, close, low, exchange, lastTradedQuantity,
                       totalBuyQuantity ,totalSellQuantity, change ,volume):
        dict_rt = {'script_token': script_token,
                   'exchange': exchange,
                   'lastTradedPrice': lastTradedPrice,
                   'lastTradedQuantity': lastTradedQuantity,
                   'totalBuyQuantity': totalBuyQuantity,
                   'totalSellQuantity': totalSellQuantity,
                   'lastTradedTime': datetime.strptime(lastTradedTime, '%d/%m/%Y %H:%M:%S'),
                   'close': close,
                   'change': change,
                   'volume': volume,
                   'low': low}
        self.data_df = self.data_df.append(dict_rt, ignore_index=True)

    def update_last_tick_time(self):
        recent_tick_time = self.data_df['lastTradedTime'].max()
        if recent_tick_time is np.NaN:
            self.latest_tick_time = None
        else:
            if self.latest_tick_time is None:
                self.latest_tick_time = recent_tick_time
            else:
                if self.latest_tick_time < recent_tick_time:
                    self.latest_tick_time = recent_tick_time
                recent_tick_time = self.connect_status_df['time'].max()
                if self.latest_tick_time < recent_tick_time:
                    self.latest_tick_time = recent_tick_time

    def fallback_ltp_price(self):
        connection = BrokerAppDetails.get_normal_connection(self.client_id)
        f = open(self.registry_file, 'r')
        lines = f.readlines()
        for line in lines:
            fields = line.split('|')
            exchange = fields[0][:3].upper()
            if len(exchange) < 3:
                continue
            token = fields[1].rstrip("\n")
            symbol = AngelSymbol.get_symbol(exchange, token)
            try:
                data_dict = connection.ltpData(exchange = exchange, tradingsymbol= symbol, symboltoken= token)
            except:
                sleep(1)
                data_dict = connection.ltpData(exchange=exchange, tradingsymbol=symbol, symboltoken=token)
            ltp = data_dict.get('data').get('ltp')
            low = data_dict.get('data').get('low')
            close = data_dict.get('data').get('close')
            ltt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if token in self.data_df.script_token.values:
                self.update_data_df(token, ltt, ltp, close, low, None, None, None, None, None)
            else:
                self.append_data_df(token, ltt, ltp, close, low, None, None, None, None, None, None)

    def restart_ticker(self):
        print('#######        RESTARTING TICKER     #######')
        self.ticker.close()
        while self.ticker.is_connected():
            sleep(1)
            print('Func : restart_ticker : Close initiated, still connected')
        self.ticker._is_first_connect = True
        self.startTicker()
        while not self.ticker.is_connected():
            sleep(1)
            print('Func : restart_ticker : One initiated, still not connected')
        print('Func : restart_ticker : CONNECTED')

    def _monitor_ticker_heartbeat(self):
        recent_status_time_series = self.connect_status_df.loc[self.connect_status_df['msg'] == 'heartbeat', 'time']
        if recent_status_time_series.empty:
            return False
        else:
            recent_status_time = recent_status_time_series[1]
        if recent_status_time > (datetime.now() - timedelta(seconds=61)):
            return False
        else:
            print('Func : _monitor_ticker_heartbeat : Last heartbeat is older than 60 second, Restarting Ticker')
            return True

    def monitor_and_fallback(self):
        while True:
            if self._monitor_ticker_heartbeat():
                self.restart_ticker()
                sleep(30)
            sleep(5)
            if self.ticker is None:
                print('Func : monitor_and_fallback : ERROR Ticker connection is None')
                print('Func : monitor_and_fallback : Starting fallback logic')
                self.fallback_ltp_price()
                print('Func : monitor_and_fallback : Trying restarting websocket')
                self.restart_ticker()
                print('Func : monitor_and_fallback : Started')
            elif self.ticker.is_connected:
                self.update_last_tick_time()
                if self.latest_tick_time is None:
                    print('Func : monitor_and_fallback : No data from websocket, Latest Tick Fail')
                    print('Func : monitor_and_fallback : Moving to fallback logic')
                    self.fallback_ltp_price()
                    continue
                if self.latest_tick_time > (datetime.now() - timedelta(seconds=5)):
                    print('Func : monitor_and_fallback : Everything looks OK')
                    continue
                else:
                    print('Func : monitor_and_fallback : Ticker connection OK, Latest Tick Fail')
                    print('Func : monitor_and_fallback : Moving to fallback logic')
                    self.fallback_ltp_price()
                    continue
            else:
                print('Func : monitor_and_fallback : Websocket not connected, Latest Tick Fail')
                print('Func : monitor_and_fallback : Moving to fallback logic')
                self.fallback_ltp_price()
                print('Func : monitor_and_fallback : Restart ticker')
                self.restart_ticker()
                continue

    def onConnect(self):
        pass
        #self.logger.info('Ticker connection successful.')

    def onDisconnect(self, code, reason):
        self.logger.error('Ticker got disconnected. code = %d, reason = %s', code, reason)

    def onError(self, code, reason):
        self.logger.error('Ticker errored out. code = %d, reason = %s', code, reason)

    def onReconnect(self, attemptsCount):
        self.logger.warn('Ticker reconnecting.. attemptsCount = %d', attemptsCount)

    def onMaxReconnectsAttempt(self):
        self.logger.error('Ticker max auto reconnects attempted and giving up..')

    def onOrderUpdate(self, data):
        # logging.info('Ticker: order update %s', data)
        pass

if __name__ == '__main__':
    from Logging.Logger import GetLogger
    logger = GetLogger().get_logger()
    obj = AngelTicker('S705342', logger)
    obj.fallback_ltp_price()
    print(obj.data_df)


