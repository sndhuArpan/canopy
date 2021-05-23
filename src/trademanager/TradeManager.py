import copy
import json
import logging
import os
import threading
import uuid

from Data_Wrappers.Angel_Broker.Angel_Broker_Wrapper import Angel_Broker_Wrapper
from src.OrderManager.AngelOrderManager import AngelOrderManager
from src.OrderManager.OrderInputParams import OrderInputParams
from src.models.TradeState import TradeState


class TradeManager:
    trades = {}  # to store all the trades
    client_stregies_map = {}

    @staticmethod
    def addNewTrade(trade):
        if trade == None:
            return
        logging.info('TradeManager: addNewTrade called for %s', trade)
        # for tr in TradeManager.trades:
        #     if tr.equals(trade):
        #         logging.warn('TradeManager: Trade already exists so not adding again. %s', trade)
        #         return
        # Add the new trade to the list
        client_list = TradeManager.client_stregies_map.get(trade.strategy)
        if not client_list:
            tFile = open(os.path.abspath('src/data/client_strategy_map.py'), 'r')
            client_strategy_data = json.loads(tFile.read())['mapping']
            client_list = []
            for i in client_strategy_data:
                if trade.strategy == i['strategy']:
                    client_list = i['client']
                    TradeManager.client_stregies_map[trade.strategy] = client_list
        for client in client_list:
            trade_obj = copy.deepcopy(trade)
            trade_obj.tradeID = uuid.uuid4()
            trade_obj.clientId = client
            client_trades = TradeManager.trades.get(client)
            if client_trades:
                client_trades[trade_obj.tradeID] = trade_obj
                TradeManager.trades[client] = client_trades
            else:
                TradeManager.trades[client] = {trade_obj.tradeID : trade_obj}
            logging.info('TradeManager: trade %s added successfully to the list', trade_obj.tradeID)
            t = threading.Thread(target=TradeManager.executeTrade, args=(trade_obj,), daemon=True)
            t.start()
            t.join()

    @staticmethod
    def executeTrade(trade):
        logging.info('TradeManager: Execute trade called for %s', trade)
        # Create order input params object and place order
        oip = OrderInputParams(trade.tradingSymbol,'3045', trade)
        try:
            order = TradeManager.getOrderManager().placeOrder(oip)
            if order.orderId:
                trade.tradeState = TradeState.PLACED
            trade.entryOrder = order
            client_trades = TradeManager.trades[trade.clientId]
            client_trades[trade.tradeID] = trade
        except Exception as e:
            logging.error('TradeManager: Execute trade failed for tradeID %s: Error => %s', trade.tradeID, str(e))
            trade.tradeState = TradeState.PLACEDERROR
            TradeManager.trades[trade.clientId][trade.tradeID] = trade
            client_list = TradeManager.client_stregies_map.get(trade.strategy)
            client_list.remove(trade.clientId)
            TradeManager.client_stregies_map[trade.strategy] = client_list
            tFile = open(os.path.abspath('src/data/client_strategy_map.py'), 'r')
            client_strategy_data = json.loads(tFile.read())
            for i in client_strategy_data['mapping']:
                if trade.strategy == i['strategy']:
                    i['client'] = client_list
                    break
            json_object = json.dumps(client_strategy_data, indent=4)
            # Writing to sample.json
            with open(os.path.abspath('src/data/client_strategy_map.py'), "w") as outfile:
                outfile.write(json_object)

        logging.info('TradeManager: Execute trade successful for %s and entryOrder %s', trade, trade.entryOrder)

    @staticmethod
    def getOrderManager():
        orderManager = AngelOrderManager('Angel','S705342')
        return orderManager

    @staticmethod
    def getClientConnect(client):
        angel = Angel_Broker_Wrapper()
        return angel.connect

    @staticmethod
    def get_placed_trade_status():
        clients = TradeManager.trades.keys()
        for client in clients:
            orders = TradeManager.trades.get(client)
            order_book = TradeManager.getClientConnect(client).orderBook().__getitem__('data')
            for order in reversed(order_book):
                ordertag = order['ordertag']
                trade = orders.get(ordertag)
                if trade:
                    trade.tradeState = order['orderstatus']
                    trade.filledQty = order['filledshares']
                    trade.startTimestamp = order['filltime']






