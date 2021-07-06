import sqlite3
import os
import pathlib

from cryptography.fernet import Fernet

from src.DB.static_db.static_db import static_db
from utils.Utils import Utils
from smartapi import SmartConnect


class Connection:

    def __init__(self, client_id, password, api_key, websocket_api_key, broker):
        self.client_id = client_id
        self.password = password
        self.api_key = api_key
        self.websocket_api_key = websocket_api_key
        self.broker = broker

    def get(self):
        return self


class BrokerAppDetails(static_db):

    def __init__(self):
        super().__init__()
        encrypt_file = os.path.join(pathlib.Path(os.path.dirname(__file__)).parents[2], 'EncryptionKey.txt')
        infile = open(encrypt_file, 'r')
        key = infile.readline()
        byte_key = bytes(key, encoding='utf8')
        self.cipher_suite = Fernet(byte_key)

        self.connection_dict = {}

    def encryt_text(self, text):
        byte_text = bytes(text, encoding='utf8')
        ciphered_text = self.cipher_suite.encrypt(byte_text)
        return ciphered_text.decode("utf-8")

    def decrypt_text(self, text):
        ciphered_bytes = bytes(text, encoding='utf8')
        unciphered_bytes = (self.cipher_suite.decrypt(ciphered_bytes))
        return unciphered_bytes.decode("utf-8")

    def create_brokerclientdetails_table(self):
        create_table = '''Create table brokerclientdetails 
                          (client_id    varchar2(20) NOT NULL PRIMARY KEY,
                           password     varchar2(400),
                           api_key      varchar(10),
                           websocket_api_key  varchar2(20),
                           broker        varchar(10))'''
        self.conn.execute(create_table)
        self.conn.commit()

    def insert_into_brokerclientdetails(self, connection):
        encrypted_password = self.encryt_text(connection.password)
        insert_query = '''insert into brokerclientdetails(client_id,password,api_key,websocket_api_key,broker) 
                         values ("{client_id}","{password}","{api_key}","{websocket_api_key}","{broker}")'''
        insert_query = insert_query.format(client_id = connection.client_id,
                                           password = encrypted_password,
                                           api_key = connection.api_key,
                                           websocket_api_key = connection.websocket_api_key,
                                           broker = connection.broker)
        print(insert_query)
        self.conn.execute(insert_query)
        self.conn.commit()

    def get_brokerclientdetails(self, client_id):
        select_query = 'select client_id,password,api_key,websocket_api_key,broker from brokerclientdetails where client_id = "{client_id}"'
        select_query = select_query.format(client_id=client_id)
        cursor = self.conn.execute(select_query)
        for row in cursor:
            if row:
                return Connection(row[0], self.decrypt_text(row[1]), row[2], row[3], row[4]).get()
            else:
                return None

    def create_normal_connection(self, client_id):
        connection_details = self.get_brokerclientdetails(client_id)
        broker = connection_details.broker
        if broker == 'ANGEL':
            connect = SmartConnect(api_key= connection_details.api_key)
            connect.generateSession(client_id, connection_details.password)
            self.connection_dict[client_id] = connect

    def check_connection_exists(self, client_id):
        if client_id in self.connection_dict.keys():
            return True, self.connection_dict.get(client_id)
        else:
            return False, None

    def get_normal_connection(self, client_id):
        connection_exists, connection = self.check_connection_exists(client_id)
        if connection_exists:
            return connection
        else:
            self.create_normal_connection(client_id)
            return self.connection_dict.get(client_id)

    def create_all_connections(self):
        all_connection_query =  '''select client_id from brokerclientdetails'''
        cursor = self.conn.execute(all_connection_query)
        for row in cursor:
            if row:
                self.create_normal_connection(row[0])


    def session_reconnect(self, client_id):
        self.create_normal_connection(client_id)

    def get_all_clients(self):
        select_query = 'select client_id from brokerclientdetails'
        cursor = self.conn.execute(select_query)
        client_list = []
        for row in cursor:
            client_list.append(row[0])
        return client_list

if __name__ == '__main__':

    obj= Connection('A533646', 'poiuhbnm@2', 'hFAupBdI', None, 'ANGEL').get()
    BrokerAppDetails().insert_into_brokerclientdetails(obj)
