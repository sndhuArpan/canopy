import numpy as np
import pandas as pd
from performance_matrix.lib.matrix_charts.PlotBasicLineChart import PlotBasicLineChart
from performance_matrix.lib.matrix_charts.SubPlotSharedXAxis import SubPlotSharedXAxis


class EquityCurve:

    def __init__(self, trade_df, initial_account_value, volatility_period, plot_dir):
        self.plot_dir = plot_dir
        self.trade_sheet = trade_df[trade_df['realised_profit'].notna()].sort_values('booked_date')
        self.initial_account_value = initial_account_value
        self.volatility_period = volatility_period
        self.wealth_and_profit_df = self.get_wealth_and_profit_df()

    def get_wealth_and_profit_df(self):
        current_wealth = self.initial_account_value
        profit = 0
        df = pd.DataFrame(columns=['booked_date', 'wealth', 'profit'])
        for index, row in self.trade_sheet.iterrows():
            booked_date = row['booked_date']
            profit = profit + row['realised_profit']
            current_wealth = current_wealth + row['realised_profit']
            df_row = {'booked_date': booked_date,
                      'wealth': current_wealth,
                      'profit': profit}
            df = df.append(df_row, ignore_index=True)
        # Compute the logarithmic returns using the Closing price
        df['log_Ret'] = np.log(df['wealth'] / df['wealth'].shift(1))
        # Compute Volatility using the pandas rolling standard deviation function
        df['volatility'] = df['log_Ret'].rolling(window=self.volatility_period).std() * np.sqrt(self.volatility_period)
        return df

    def generate_equity_wealth_curve(self):
        plot_dict = {'x_axis_values': self.wealth_and_profit_df['booked_date'],
                     'y_axis_values': self.wealth_and_profit_df['wealth'],
                     'x_axis_label' : 'Account Date',
                     'y_axis_label': 'Account value',
                     'title' : 'Equity Curve by Initial Account :' + str(self.initial_account_value),
                     'image_file': 'Equity_To_Wealth_Graph'
                     }
        plot_obj = PlotBasicLineChart(**plot_dict)
        image_path = plot_obj.get_image(self.plot_dir)
        return image_path

    def generate_equity_profit_curve(self):
        plot_dict = {'x_axis_values': self.wealth_and_profit_df['booked_date'],
                     'y_axis_values': self.wealth_and_profit_df['profit'],
                     'x_axis_label': 'Account Date',
                     'y_axis_label': 'Profit',
                     'title': 'Equity Curve by Trade Profit',
                     'image_file': 'Equity_To_Profit_Graph'
                     }
        plot_obj = PlotBasicLineChart(**plot_dict)
        image_path = plot_obj.get_image(self.plot_dir)
        return image_path

    def generate_volatility_return_graph(self):
        plot_dict = {'x_axis_values': self.wealth_and_profit_df['booked_date'],
                     'upper_y_axis_values': self.wealth_and_profit_df['wealth'],
                     'lower_y_axis_values': self.wealth_and_profit_df['volatility'],
                     'upper_fill_between_color': 'green',
                     'lower_fill_between_color': 'red',
                     'x_axis_label': 'Account Date',
                     'upper_y_label': 'wealth',
                     'lower_y_label': 'volatility',
                     'title': 'Return by Volatility',
                     'image_file': 'Return_By_Volatility_Graph'}
        plot_obj = SubPlotSharedXAxis(**plot_dict)
        image_path = plot_obj.get_image(self.plot_dir)
        return image_path