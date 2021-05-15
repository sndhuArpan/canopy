import pandas as pd
from datetime import timedelta
from performance_matrix.lib.matrix_charts.SubPlotSharedXAxis import SubPlotSharedXAxis


class AccountUtilization:

    def __init__(self, trade_df, initial_account_value, plot_dir):
        self.plot_dir = plot_dir
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
        account_util = account_util[account_util.amount_utilized_percentage != 0]
        account_util = account_util[account_util.active_trades != 0]
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
                     'upper_y_axis_values': self.account_util_df['amount_utilized_percentage'],
                     'lower_y_axis_values': self.account_util_df['active_trades'],
                     'x_axis_label': 'Account Date',
                     'upper_y_label': 'Account Util %',
                     'lower_y_label': 'Trades',
                     'title': 'Account_Utilization_Graph',
                     'image_file': 'Account_Utilization_Graph.jpeg'}
        plot_obj = SubPlotSharedXAxis(**plot_dict)
        image_path = plot_obj.get_image(self.plot_dir)
        return image_path



