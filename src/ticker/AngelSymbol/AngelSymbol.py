import requests
import csv
import pandas as pd
from datetime import datetime
import os, shutil

import warnings
warnings.filterwarnings("ignore")

class AngelSymbol:
    now = datetime.now()
    date_str = now.strftime("%d%m%Y")
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    def __init__(self):
        pass

    @staticmethod
    def create_dir_if_not_exist():
        print('Func :create_dir_if_not_exist : In')
        if not os.path.isdir(AngelSymbol.data_dir):
            print('Func :create_dir_if_not_exist : Creating Data directory')
            os.makedirs(AngelSymbol.data_dir)
        print('Func :create_dir_if_not_exist : exit')

    @staticmethod
    def get_file_name(exch_seg):
        return os.path.join(AngelSymbol.data_dir, exch_seg + AngelSymbol.date_str + '.csv')

    @staticmethod
    def clean_dir(folder):
        print('Func :clean_dir : In')
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        print('Func : Folder cleaned %s : exit' % folder)

    @staticmethod
    def create_angle_symbol_csv():
        print('Func :create_angle_symbol_csv : In')
        AngelSymbol.create_dir_if_not_exist()
        file_name = os.path.join(AngelSymbol.data_dir, 'symbol' + AngelSymbol.date_str + '.csv')
        print('Func :create_angle_symbol_csv : Check main symbol file exists')
        if os.path.isfile(file_name):
            print('Func :create_angle_symbol_csv : File exists true, returning df')
            return pd.read_csv(file_name)
        else:
            print('Func :create_angle_symbol_csv : cleaning main data folder %s' % AngelSymbol.data_dir)
            AngelSymbol.clean_dir(AngelSymbol.data_dir)
            url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
            r = requests.get(url)
            data = r.json()
            keys = data[0].keys()
            file_name = os.path.join(AngelSymbol.data_dir, 'symbol' + AngelSymbol.date_str + '.csv')
            a_file = open(file_name, "w")
            print('Func :create_angle_symbol_csv : Creating main symbol file %s' % file_name)
            dict_writer = csv.DictWriter(a_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
            a_file.close()
            print('Func :create_angle_symbol_csv : Returning dataframe from function')
            df = pd.read_csv(file_name)
            return df

    @staticmethod
    def create_csv_by_segment():
        print('Func :create_csv_by_segment : Checking if todays files exists')
        file_name = AngelSymbol.get_file_name('NSE')
        # check if today's file exist
        if os.path.isfile(file_name):
            print('Func :create_csv_by_segment : Files exists, True')
            return None
        print('Func :create_csv_by_segment : Files exists : False')
        df = AngelSymbol.create_angle_symbol_csv()
        print('Func :create_csv_by_segment : Splitting instrument file on exchange basis')
        splits = list(df.groupby("exch_seg"))
        for i in splits:
            exch_seg = i[0]
            file_name=AngelSymbol.get_file_name(exch_seg)
            print('Func :create_csv_by_segment : Creating file %s' % file_name)
            i[1].to_csv(file_name)
        main_symbol_file = os.path.join(AngelSymbol.data_dir, 'symbol' + AngelSymbol.date_str + '.csv')
        print('Func :create_csv_by_segment : Removing main symbol file %s' % main_symbol_file )
        os.remove(main_symbol_file)

    @staticmethod
    def get_symbol_token(exchange, name):
        print('Func :get_symbol_token : In')
        print('Func :get_symbol_token : For exchange %s and name %s' % (exchange, name))
        file_name = exchange + AngelSymbol.date_str + '.csv'
        file_abs_name = os.path.join(AngelSymbol.data_dir, file_name)
        symbol_dataframe = pd.read_csv(file_abs_name)
        symbol = symbol_dataframe[symbol_dataframe['symbol'] == name]
        if symbol.empty:
            print('Func :get_symbol_token : No Symbol found')
            return None
        else:
            print('Func :get_symbol_token : Return token, exit')
            return symbol['token'].iloc[0]

    @staticmethod
    def get_share_name(exchange, token):
        print('Func :get_share_name : In')
        print('Func :get_share_name : For exchange %s and token %s' % (exchange, token))
        file_name = exchange + AngelSymbol.date_str + '.csv'
        file_abs_name = os.path.join(AngelSymbol.data_dir, file_name)
        symbol_dataframe = pd.read_csv(file_abs_name)
        symbol = symbol_dataframe[symbol_dataframe['token'] == token]
        if symbol.empty:
            print('Func :get_share_name : No share name found')
            return None
        else:
            print('Func :get_share_name : Return share name, exit')
            return symbol['name'].iloc[0]



if __name__ == '__main__':
    AngelSymbol.create_csv_by_segment()
    print(AngelSymbol.get_symbol_token('NSE', 'MARUTI-EQ'))
    print(AngelSymbol.get_share_name('NSE', 10999))