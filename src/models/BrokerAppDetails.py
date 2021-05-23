from re import search
from utils.Utils import Utils
from smartapi import SmartConnect
from smartapi import WebSocket
import pandas as pd



class BrokerAppDetails:

    connection_dict = {}
    abs_config_path = '/Users/Sandhu/canopy/canopy/broker_detail.cfg'

    @staticmethod
    def get_connection_details(client_id):
        connection_details = Utils.get_config_dict(BrokerAppDetails.abs_config_path, client_id)
        return connection_details

    @staticmethod
    def create_normal_connection(client_id):
        connection_details = BrokerAppDetails.get_connection_details(client_id)
        broker = connection_details.get('broker')
        if broker == 'ANGEL':
            connect = SmartConnect(api_key= connection_details.get('api_key'))
            connect.generateSession(client_id, connection_details.get('password'))
            #connect.setSessionExpiryHook(BrokerAppDetails.session_reconnect(client_id))
            BrokerAppDetails.connection_dict[client_id] = connect

    @staticmethod
    def check_connection_exists(client_id):
        if client_id in BrokerAppDetails.connection_dict.keys():
            return True, BrokerAppDetails.connection_dict.get(client_id)
        else:
            return False, None

    @staticmethod
    def get_normal_connection(client_id):
        connection_exists, connection = BrokerAppDetails.check_connection_exists(client_id)
        if connection_exists:
            return connection
        else:
            BrokerAppDetails.create_normal_connection(client_id)
            return BrokerAppDetails.connection_dict.get(client_id)

    @staticmethod
    def create_all_connections():
        client_ids = Utils.get_all_config_section(BrokerAppDetails.abs_config_path)
        for id in client_ids:
            BrokerAppDetails.create_normal_connection(id)

    @staticmethod
    def session_reconnect(client_id):
        BrokerAppDetails.create_normal_connection(client_id)


if __name__ == '__main__':
    import time
    BrokerAppDetails.create_all_connections()
    connection = BrokerAppDetails.connection_dict.get('S705342')
    while True:
        time.sleep(10)
        connection.renewAccessToken()
        print(connection.access_token)