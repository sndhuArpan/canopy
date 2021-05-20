## WebSocket
from smartapi import WebSocket
from smartapi import SmartConnect


obj = SmartConnect(api_key="QT0dWWIa")
obj.generateSession("S705342","poiuhbnm@2")
feedToken = obj.getfeedToken()
token = "mcx_fo|229650"  # "nse_cm|2885&nse_cm|1594&nse_cm|11536"
task = "mw"
def on_tick(ws, tick):
    print("Ticks: {}".format(tick))


def on_connect(ws, response):
    ws.websocket_connection()  # Websocket connection
    ws.send_request(token, task)


def on_close(ws, code, reason):
    ws.stop()


# Assign the callbacks.


if __name__ == '__main__':
    CLIENT_CODE = "S705342"
    ss = WebSocket(feedToken, CLIENT_CODE)

    ss.on_ticks = on_tick
    ss.on_connect = on_connect
    ss.on_close = on_close

    ss.connect()
    print('done')