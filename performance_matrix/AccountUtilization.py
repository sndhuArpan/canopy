import numpy as np
import pandas as pd
from datetime import timedelta
from performance_matrix.matrix_charts.PlotSharedXAxisTwoYAxis import PlotSharedXAxisTwoYAxis


class AccountUtilization:

    def __init__(self, trade_df, initial_account_value):
        self.trade_sheet = trade_df[trade_df['realised_profit'].notna()]
        self.initial_account_value = initial_account_value
        self.account_util_df = self.account_utilization()

    def account_utilization(self):
        get_min_date = self.trade_sheet['entry_datetime'].min()
        get_max_date = self.trade_sheet['booked_date'].dropna().max()
        that_date = get_min_date.replace(hour=23, minute=00, second= 00)
        that_date1 =get_min_date.replace(hour=00, minute=00, second= 00)
        account_util = pd.DataFrame(columns= ['account_date', 'amount_utilized_percentage', 'active_trades'])
        for i in range((get_max_date - get_min_date).days):
            rslt_df = self.trade_sheet[(self.trade_sheet['entry_datetime'] <= that_date) &
                                       (self.trade_sheet['booked_date'] >= that_date1)]
            active_trades = len(rslt_df.index)
            amount_utilized = (rslt_df['buy_value'].sum()/self.initial_account_value)*100
            record_dict = {'account_date': that_date1,
                           'amount_utilized_percentage': amount_utilized,
                           'active_trades': active_trades}
            that_date = that_date + timedelta(days=1)
            that_date1 = that_date1 + timedelta(days=1)
            account_util = account_util.append(record_dict, ignore_index=True)
        return account_util

    def account_utilization_matrix(self):
        max_amount_utilized_percentage = self.account_util_df['amount_utilized_percentage'].max()
        min_amount_utilized_percentage = self.account_util_df['amount_utilized_percentage'].min()
        average_amount_utilized_percentage = self.account_util_df['amount_utilized_percentage'].mean()
        max_trades_active = self.account_util_df['active_trades'].max()
        min_trades_active = self.account_util_df['active_trades'].min()
        average_trades_active = self.account_util_df['active_trades'].mean()
        return {'max_amount_utilized_percentage': max_amount_utilized_percentage,
                'min_amount_utilized_percentage': min_amount_utilized_percentage,
                'average_amount_utilized_percentage': average_amount_utilized_percentage,
                'max_trades_active': max_trades_active,
                'min_trades_active': min_trades_active,
                'average_trades_active': average_trades_active}

    def plot_graph(self):
        plot_dict = {'x_axis_values': self.account_util_df['account_date'],
                     'right_y_axis_values': self.account_util_df['active_trades'],
                     'left_y_axis_values': self.account_util_df['amount_utilized_percentage'],
                     'x_axis_label' : 'Account Date',
                     'right_y_label': 'Active Trades',
                     'left_y_label' : 'Amount Utilized Percentage',
                     'title' : 'Initial Account :' + str(self.initial_account_value),
                     'image_file': 'Account_Utilization_Graph'
                     }
        plot_obj = PlotSharedXAxisTwoYAxis(**plot_dict)
        plot_obj.get_image()



