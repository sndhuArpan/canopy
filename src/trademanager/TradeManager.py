import logging
import threading
import time

from Data_Wrappers.Angel_Broker.Angel_Broker_Wrapper import Angel_Broker_Wrapper
from src.DB.canopy.canopy_db import canopy_db, trade_status_model
from src.OrderManager.AngelOrderManager import AngelOrderManager
from src.OrderManager.OrderInputParams import OrderInputParams
from src.models.OrderStatus import OrderStatus
from src.models.OrderType import OrderType
from src.models.Variety import Variety


class TradeManager:

    @staticmethod
    def addNewTrade(trade):
        if trade==None:
            return
        logging.info('TradeManager: addNewTrade called for %s', trade)
        sql = canopy_db()
        model = trade_status_model(trade.strategy)
        model.initialize_values(client_id=trade.clientId, strategy_trade_id=trade.strategy_trade_id, system_trade_id=trade.system_tradeID,
                                order_type=trade.orderType,
                                order_status=OrderStatus.OPEN_PENDING,
                                transaction_type=trade.direction,
                                share_name=trade.tradingSymbol,
                                qty=trade.qty,
                                stoploss=trade.stopLoss,
                                price=trade.requestedEntry,
                                instrument_type=trade.instrument_type)
        sql.insert_strategy_daily(model)
        logging.info('TradeManager: trade %s added successfully to the list', trade.system_tradeID)
        t = threading.Thread(target=TradeManager.executeTrade, args=(trade,), daemon=True)
        t.start()
        t.join()

    @staticmethod
    def executeTrade(trade):
        logging.info('TradeManager: Execute trade called for %s', trade)
        # Create order input params object and place order
        print('in excute trade')
        oip = OrderInputParams(trade.tradingSymbol, '14366', trade)
        sql = canopy_db()
        model = sql.select_daily_entry_system_trade_id(trade.system_tradeID, trade.strategy)
        try:
            order = TradeManager.getOrderManager().placeOrder(oip)
            model.order_id = order.orderId
            model.order_status = OrderStatus.CREATED
            print('in excute trade placed')
            sql.update_daily_entry(model)
            logging.info('TradeManager: Execute trade successful for %s and orderId %s', trade.system_tradeID,
                         order.orderId)
        except Exception as e:
            print('in excute trade failed')
            logging.error('TradeManager: Execute trade failed for tradeID %s: Error => %s', trade.system_tradeID,
                          str(e))
            model.order_status = OrderStatus.REJECTED
            sql.update_daily_entry_status(model)

    @staticmethod
    def executeCancelTrade(model):
        logging.info('TradeManager: Cancel trade called for %s', model.order_id)
        # Create order input params object and place order
        variety = ''
        if model.order_type in (OrderType.LIMIT,OrderType.MARKET):
            variety = Variety.NORMAL
        else:
            variety = Variety.STOPLOSS
        try:
            sql = canopy_db()
            oip = OrderInputParams()
            oip.variety = variety
            oip.orderId = model.order_id
            status = TradeManager.getOrderManager().cancelOrder(oip)
            if status:
                model.order_status = OrderStatus.CANCELLED
            else:
                model.order_status = OrderStatus.FAILED
            sql.update_daily_entry_status(model)
        except Exception as e:
            logging.error('TradeManager: Cancel trade failed for tradeID %s: Error => %s', model.system_trade_id,
                          str(e))
            model.order_status = OrderStatus.FAILED
            sql.update_daily_entry_status(model)

    @staticmethod
    def getOrderManager():
        orderManager = AngelOrderManager('Angel', 'S705342')
        return orderManager

    @staticmethod
    def getClientConnect(client):
        angel = Angel_Broker_Wrapper()
        return angel.connect

    @staticmethod
    def update_trade_status():
        while True:
            sql = canopy_db()
            strategy_name = 'SampleStrategy'
            order_status_list = '"created", "open"'
            client_list = sql.select_distinct_client_id(strategy_name)
            for client in client_list:
                order_book_dict = {}
                orders_list = sql.select_daily_entry_client_id_order_status(client, strategy_name, order_status_list)
                connect = TradeManager.getClientConnect(client)
                order_data = connect.orderBook().__getitem__('data')
                if order_data:
                    for data in order_data:
                        order_book_dict[data['orderid']] = data

                    for order in orders_list:
                        order_info = order_book_dict.get(order.order_id)
                        order.order_status = order_info['orderstatus']
                        order.price = order_info['averageprice']
                        order.fill_qty = order_info['filledshares']
                        order.fill_time = order_info['updatetime']
                        sql = canopy_db()
                        sql.update_daily_entry_filled(order)
            time.sleep(120)

    @staticmethod
    def get_trade(strategy, system_tradeID):
        sql = canopy_db()
        return sql.select_daily_entry_system_trade_id(system_tradeID, strategy)
