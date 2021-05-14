import os
from pathlib import Path
import ast
import pandas as pd
import numpy as np
import configparser as cfg_parser

class TransformTradeSheet:

    def __init__(self, full_trade_sheet_path, run_type):
        self.run_type = run_type
        self.full_trade_sheet_path = full_trade_sheet_path
        self.trade_sheet_path = self.generate_report_dir()
        self.config_dict = self._get_config_dict()
        self.trade_sheet_df = self._create_df()
        self.transform_sheet_df = pd.DataFrame(columns= ast.literal_eval(self.config_dict.get('transform_trade_sheet_columns')))
        self.transform_sheet_df.set_index('system_trade_id')

    def generate_report_dir(self):
        dir = os.path.splitext(os.path.basename(self.full_trade_sheet_path))[0]
        final_dir =  os.path.join(os.path.join(os.path.join(Path(__file__).parent.parent, 'performance_report/temp/'), dir),
                                  self.run_type)
        if os.path.isdir(final_dir):
            return final_dir
        else:
            os.makedirs(final_dir, exist_ok=True)
            return final_dir

    def _get_config_dict(self):
        self.config = cfg_parser.RawConfigParser()
        self.current_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent
        self.config_path = os.path.join(self.current_dir, 'config/config.cfg')
        self.config.read(self.config_path)
        return dict(self.config.items('GLOBAL'))

    def _create_df(self):
        trade_sheet_df = pd.read_csv(self.full_trade_sheet_path, skip_blank_lines=True)
        required_column_list = ast.literal_eval(self.config_dict.get('trade_book_columns'))
        trade_sheet_df = trade_sheet_df[required_column_list]
        return trade_sheet_df

    def _yield_system_trade_data(self):
        unique_system_trade_id = self.trade_sheet_df.system_trade_id.unique()
        for system_trade_id in unique_system_trade_id:
            yield self.trade_sheet_df.loc[self.trade_sheet_df['system_trade_id'] == system_trade_id]

    @staticmethod
    def get_trade_status(df_per_system_trade_id):
        quantity = 0
        for index, row in df_per_system_trade_id.iterrows():
            if row['trade_type'] == 'buy':
                quantity = quantity + row['quantity']
            if row['trade_type'] == 'sell':
                quantity = quantity - row['quantity']
        if quantity == 0:
            return 'closed'
        else:
            return 'open'

    @staticmethod
    def get_exit_datetime(df_per_system_trade_id, trade_status):
        if trade_status == 'closed':
            return df_per_system_trade_id['order_execution_time'].iloc[-1]
        else:
            return np.NaN

    @staticmethod
    def get_trade_value(df_per_system_trade_id, trade_type):
        trade_value = 0
        for index, row in df_per_system_trade_id.iterrows():
            if row['trade_type'] == trade_type:
                trade_value = trade_value + (row['price'] * row['quantity'])
        if trade_value == 0:
            return np.NaN
        else:
            return trade_value

    @staticmethod
    def get_opposite_trade(trade_type):
        if trade_type == 'buy':
            return 'sell'
        else:
            return 'buy'

    @staticmethod
    def get_booked_value(df_per_system_trade_id, trade_status, trade_type, buy_value, sell_value):
        trade_df = df_per_system_trade_id.loc[df_per_system_trade_id['trade_type'] == trade_type]
        counter_trade_df = df_per_system_trade_id.loc[df_per_system_trade_id['trade_type'] ==
                                                      TransformTradeSheet.get_opposite_trade(trade_type)]
        booked_date = df_per_system_trade_id['order_execution_time'].iloc[-1]
        if trade_status == 'closed':
            if trade_type == 'buy':
                return buy_value, trade_df['quantity'].sum(), booked_date
            if trade_type == 'sell':
                return sell_value, trade_df['quantity'].sum(), booked_date
        else:
            if counter_trade_df.empty:
                return np.NaN, np.NaN, np.NaN
            else:
                total_counter_quantity = counter_trade_df['quantity'].sum()
                return_total_counter_quantity = total_counter_quantity
                total_counter_value = 0
                for index, row in counter_trade_df.iterrows():
                    total_counter_value = total_counter_value + row['quantity'] * row['price']
                avg_counter_square_price =  total_counter_value/total_counter_quantity
                if TransformTradeSheet.get_opposite_trade(trade_type) == 'sell':
                    total_counter_quantity = total_counter_quantity * -1
            booked_value = 0
            for index, row in trade_df.iterrows():
                temp_quantity = 0
                temp_value = 0
                if trade_type == 'sell':
                    temp_quantity = row['quantity'] * -1
                else:
                    temp_quantity = row['quantity']
                if abs(total_counter_quantity) < abs(temp_quantity):
                    booked_value = booked_value + (row['price'] * abs(total_counter_quantity))
                    break
                else:
                    booked_value = booked_value + abs(row['price'] * temp_quantity)
                    total_counter_quantity = total_counter_quantity + temp_quantity
            return booked_value, return_total_counter_quantity, booked_date

    @staticmethod
    def get_profit(trade_status, trade_type, booked_value, buy_value, sell_value):
        if booked_value is None:
            return np.NaN, np.NaN
        if trade_type == 'buy':
            return sell_value - booked_value, ((sell_value - booked_value)/booked_value)*100
        if trade_type == 'sell':
            return buy_value - booked_value, ((buy_value - booked_value)/booked_value)*100

    def _insert_transform_sheet_details(self, df_per_system_trade_id):
        df_per_system_trade_id = df_per_system_trade_id.copy()
        df_per_system_trade_id["order_execution_time"] = pd.to_datetime(df_per_system_trade_id["order_execution_time"])
        df_per_system_trade_id = df_per_system_trade_id.sort_values(by="order_execution_time")
        system_trade_id = df_per_system_trade_id['system_trade_id'].iloc[0]
        symbol = df_per_system_trade_id['symbol'].iloc[0]
        trade_type = df_per_system_trade_id['trade_type'].iloc[0]
        interval = df_per_system_trade_id['interval'].iloc[0]
        quantity = df_per_system_trade_id.loc[df_per_system_trade_id['trade_type'] == trade_type, 'quantity'].sum()
        trade_status = TransformTradeSheet.get_trade_status(df_per_system_trade_id)
        entry_datetime = df_per_system_trade_id['order_execution_time'].iloc[0]
        exit_datetime = TransformTradeSheet.get_exit_datetime(df_per_system_trade_id, trade_status)
        buy_value = TransformTradeSheet.get_trade_value(df_per_system_trade_id, 'buy')
        sell_value = TransformTradeSheet.get_trade_value(df_per_system_trade_id, 'sell')
        booked_value, booked_quantity, booked_date = TransformTradeSheet.get_booked_value(df_per_system_trade_id,
                                                                                          trade_status, trade_type,
                                                                                          buy_value, sell_value)
        realised_profit, profit_percentage = TransformTradeSheet.get_profit(trade_status, trade_type, booked_value, buy_value, sell_value)
        stop_value = df_per_system_trade_id['stop_loss'].iloc[0] * booked_quantity
        if sell_value - booked_value <= 1:
            reward = np.NaN
        else:
            reward = sell_value - booked_value
        risk_reward_ratio = (booked_value - stop_value)/reward
        record_dict = {'system_trade_id': system_trade_id, 'symbol': symbol, 'trade_type' : trade_type,
                       'interval' : interval, 'quantity' : quantity, 'trade_status' : trade_status,
                       'entry_datetime' : entry_datetime, 'buy_value' : buy_value , 'exit_datetime' : exit_datetime,
                       'sell_value': sell_value, 'stop_value': stop_value, 'booked_value' : booked_value,
                       'realised_profit' : realised_profit, 'booked_quantity' : booked_quantity,
                       'risk_reward_ratio' : risk_reward_ratio, 'booked_date' : booked_date,
                       'profit_percentage': profit_percentage}
        self.transform_sheet_df = self.transform_sheet_df.append(record_dict, ignore_index=True)

    def transform_trade_sheet(self):
        for df_per_system_trade_id in self._yield_system_trade_data():
            self._insert_transform_sheet_details(df_per_system_trade_id)
        #self.transform_sheet_df = self.transform_sheet_df.fillna(None)
        self.transform_sheet_df.to_csv(os.path.join(self.trade_sheet_path, 'trade_sheet.csv'), date_format='%Y-%m-%dT%H:%M:%S' ,index=False)
        return os.path.join(self.trade_sheet_path, 'trade_sheet.csv')

if __name__ == '__main__':
    print(os.path.join(Path(__file__).parent, '../performance_report/temp/'))



