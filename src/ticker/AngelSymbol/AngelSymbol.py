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
    data_dir = os.path.join(os.path.curdir, 'data')

    def __init__(self):
        pass

    @staticmethod
    def get_file_name(exch_seg):
        return os.path.join(AngelSymbol.data_dir, exch_seg + AngelSymbol.date_str + '.csv')

    @staticmethod
    def clean_dir(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    @staticmethod
    def create_angle_symbol_csv():
        file_name = os.path.join(AngelSymbol.data_dir, 'symbol' + AngelSymbol.date_str + '.csv')
        # check if today's file exist
        if os.path.isfile(file_name):
            return pd.read_csv(file_name)
        else:
            AngelSymbol.clean_dir(AngelSymbol.data_dir)
            url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
            r = requests.get(url)
            data = r.json()
            keys = data[0].keys()
            file_name = os.path.join(AngelSymbol.data_dir, 'symbol' + AngelSymbol.date_str + '.csv')
            a_file = open(file_name, "w")
            dict_writer = csv.DictWriter(a_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
            a_file.close()
            df = pd.read_csv(file_name)
            return df

    @staticmethod
    def create_csv_by_segment():
        file_name = AngelSymbol.get_file_name('NSE')
        # check if today's file exist
        if os.path.isfile(file_name):
            return None
        df = AngelSymbol.create_angle_symbol_csv()
        splits = list(df.groupby("exch_seg"))
        for i in splits:
            exch_seg = i[0]
            file_name=AngelSymbol.get_file_name(exch_seg)
            i[1].to_csv(file_name)
        os.remove(os.path.join(AngelSymbol.data_dir, 'symbol' + AngelSymbol.date_str + '.csv'))

    @staticmethod
    def get_symbol_token(exchange, name):
        file_name = exchange + AngelSymbol.date_str + '.csv'
        file_abs_name = os.path.join(AngelSymbol.data_dir, file_name)
        symbol_dataframe = pd.read_csv(file_abs_name)
        symbol = symbol_dataframe[symbol_dataframe['symbol'] == name]
        if symbol.empty:
            return None
        else:
            return symbol['token'].iloc[0]

    @staticmethod
    def get_share_name_token(exchange, token):
        file_name = exchange + AngelSymbol.date_str + '.csv'
        file_abs_name = os.path.join(AngelSymbol.data_dir, file_name)
        symbol_dataframe = pd.read_csv(file_abs_name)
        symbol = symbol_dataframe[symbol_dataframe['token'] == token]
        if symbol.empty:
            return None
        else:
            return symbol['name'].iloc[0]



if __name__ == '__main__':
    AngelSymbol.create_csv_by_segment()
    print(AngelSymbol.get_symbol_token('NSE', 'MARUTI-EQ'))
    print(AngelSymbol.get_share_name_token('NSE', 10999))