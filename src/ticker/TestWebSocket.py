from src.ticker.AngelTicker import AngelTicker
from Logging.Logger import GetLogger
import time
import threading



logger = GetLogger().get_logger()

count = 0
while True:
    count = count + 1
    obj = AngelTicker('S705342', logger)
    obj.startTicker()
    if obj.ticker.is_connected():
        print('Connected %d' % count)
    del obj
    time.sleep(5)

def send_signal():
    time.sleep(50)
    obj.ticker.websocket_connection()
#print(obj.ticker._is_first_connect)
t = threading.Thread(target=obj.monitor_and_fallback, daemon= True)
t.start()
t1 = threading.Thread(target= send_signal)
#t1.start()
while True:
    time.sleep(5)
    print(obj.connect_status_df)
    print(obj.data_df)
# obj.ticker.close()
# while obj.ticker.is_connected():
#     time.sleep(1)
#     print('still connected')
# obj.ticker._is_first_connect = True
# obj.startTicker()
# print(obj.feedToken)
# while not obj.ticker.is_connected():
#     time.sleep(1)
#     print('still not connected')
# while True:
#     time.sleep(5)
#     print(obj.data_df)
#     print(obj.connect_status_df)
# print(obj.ticker._is_first_connect)
# #print(obj.data_df)
# #obj.ticker.heartbeat()
# while True:
#     time.sleep(5)
# #t = threading.Thread(target=obj.monitor_and_fallback, daemon= True)
# #t.start()
# print('Next line')
#obj.unregisterSymbols('mcx_fo',228745)
# time.sleep(10)
# print(obj.ticker.is_connected())
# obj.connect.terminateSession('S705342')
# time.sleep(10)
# obj.startTicker()
# print(obj.ticker.is_connected())
# while True:
#     time.sleep(5)
#     print(obj.data_df)
# t.join()


