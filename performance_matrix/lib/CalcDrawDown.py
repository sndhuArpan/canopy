import random
import pandas as pd
import numpy as np
from performance_matrix.lib.TransfromTradeSheet import TransformTradeSheet
from performance_matrix.lib.matrix_charts.SubPlotSharedXAxis import SubPlotSharedXAxis
from performance_matrix.lib.GetTradeCount import GetTradeCount

class CalcDrawDown:

    def __init__(self, transformed_trade_sheet_df, initial_account_value, plot_dir):
        self.plot_dir = plot_dir
        self.maximum_drawdown = None
        self.max_drawdown_date = None
        self.draw_down_start_time = None
        self.draw_down_end_time = None
        self.draw_down_time = None
        self.draw_down_trade_number = None
        self.recovery_time = None
        self.recovery_trade_number = None
        self.trade_sheet_df = transformed_trade_sheet_df.sort_values('booked_date')
        self.initial_account_value = initial_account_value
        self.wealth_df = self.create_wealth_df().sort_index()
        self.wealth_peaks_drawdown_dict = self.draw_down()
        self.get_max_drawdown()
        self.drawdown_start_end_time()
        self.get_draw_down_and_recovery_time()
        self.get_draw_down_and_recovery_trades()

    def create_wealth_df(self):
        current_wealth = self.initial_account_value
        df = pd.DataFrame(columns=['booked_date', 'wealth', 'wealth_change_percentage'])
        for index, row in self.trade_sheet_df.iterrows():
            if np.isnan(row['realised_profit']):
                continue
            booked_date = row['booked_date']
            wealth_change_percentage = (row['realised_profit']/current_wealth)*100
            current_wealth = current_wealth + row['realised_profit']
            df_row = {'booked_date' : booked_date,
                      'wealth' : current_wealth,
                      'wealth_change_percentage' : wealth_change_percentage}
            df = df.append(df_row, ignore_index= True)
        df = df.set_index('booked_date', inplace=False)
        return df


    def draw_down(self):
        """
        Documentation String:
        Takes a Timeseries of Equity return.
        Computes and returns a Data frame with:
        1. Wealth index
        2. Previous peaks
        3. Percentage Drawdown
        """
        #return_series = self.wealth_df['wealth_change_percentage']
        #wealth_index = self.initial_account_value * (1 + return_series).cumprod()
        wealth_index = self.wealth_df['wealth']
        previous_peaks = wealth_index.cummax()
        drawdown = ((wealth_index - previous_peaks) / previous_peaks)*100

        return pd.DataFrame({
            "wealth": wealth_index,
            "peaks": previous_peaks,
            "drawdown": drawdown
        })

    def draw_down_wealth_index_plot(self):
        wealth_series = self.wealth_peaks_drawdown_dict.get('wealth')
        drawdown_series = self.wealth_peaks_drawdown_dict.get('drawdown')
        plot_dict = {'x_axis_values': wealth_series.index,
                     'upper_y_axis_values': wealth_series.values,
                     'lower_y_axis_values': drawdown_series.values,
                     'upper_fill_between_color': 'green',
                     'lower_fill_between_color' : 'red',
                     'x_axis_label': 'Account Date',
                     'upper_y_label': 'wealth',
                     'lower_y_label': 'drawdown',
                     'title': 'Portfolio Drawdown',
                     'image_file' : 'drawdown_to_wealth_graph.jpeg'
                     }
        plot_obj = SubPlotSharedXAxis(**plot_dict)
        image_path = plot_obj.get_image(self.plot_dir)
        return image_path

    def get_max_drawdown(self):
        drawdown_series = self.wealth_peaks_drawdown_dict.get('drawdown')
        self.maximum_drawdown =  min(drawdown_series)
        self.max_drawdown_date = drawdown_series.idxmin()
        #max_drawdown_date = drawdown_series[drawdown_series == maximum_drawdown].index[0]

    def drawdown_start_end_time(self):
        last_zero_dt = None
        current_zero_dt = self.wealth_peaks_drawdown_dict.get('drawdown').index[0]
        for items in self.wealth_peaks_drawdown_dict.get('drawdown').iteritems():
            if items[0] <= self.max_drawdown_date:
                if items[1] == 0:
                    current_zero_dt = items[0]
            else:
                if items[1] == 0:
                    last_zero_dt = items[0]
                    break
        self.draw_down_start_time = current_zero_dt
        self.draw_down_end_time = last_zero_dt

    def get_draw_down_and_recovery_time(self):
        if self.max_drawdown_date is None or self.draw_down_start_time is None:
            self.draw_down_time = None
        else:
            self.draw_down_time = (self.max_drawdown_date - self.draw_down_start_time).days
        if self.draw_down_end_time is None or self.max_drawdown_date is None:
            self.recovery_time = None
        else:
            self.recovery_time = (self.draw_down_end_time - self.max_drawdown_date).days

    def get_draw_down_and_recovery_trades(self):
        trade_count_obj = GetTradeCount(self.trade_sheet_df)
        if self.draw_down_start_time is None or  self.max_drawdown_date is None:
            self.draw_down_trade_number = None
        else:
            self.draw_down_trade_number = trade_count_obj.trade_count(self.draw_down_start_time, self.max_drawdown_date)
        if self.max_drawdown_date is None or self.draw_down_end_time is None:
            self.recovery_trade_number = None
        else:
            self.recovery_trade_number = trade_count_obj.trade_count(self.max_drawdown_date, self.draw_down_end_time)

    def get_all_drawdowns(self):
        initial_value = 0
        portfolio_value = []
        random_values = random.sample(range(-600, 600), 40)
        for i in random_values:
            initial_value = initial_value + i
            portfolio_value.append(initial_value)
        print(portfolio_value)

        start_value = 0
        end_value = 0
        tuple_list = []
        drawdown = False
        val_tuple = ()
        portfolio_value.insert(0, 0)
        for i, val in enumerate(portfolio_value):
            if i == 0:
                continue
            else:
                if val < portfolio_value[i - 1] and drawdown is False:
                    start_value = portfolio_value[i - 1]
                    drawdown = True
                else:
                    if drawdown is True and val > portfolio_value[i - 1]:
                        drawdown = False
                        end_value = portfolio_value[i - 1]
                        tuple_list.append([start_value, end_value])

        print(tuple_list)
        final_list = []
        start_value = tuple_list[0][0]
        end_value = tuple_list[0][1]
        i = 1
        while i < len(tuple_list):
            if start_value >= tuple_list[i][0]:
                if end_value > tuple_list[i][1]:
                    end_value = tuple_list[i][1]
                i = i + 1
            else:
                final_list.append([start_value, end_value])
                start_value = tuple_list[i][0]
                end_value = tuple_list[i][1]
        final_list.append([start_value, end_value])
        print(final_list)



if __name__ == '__main__':
    obj = TransformTradeSheet('/Users/Sandhu/Downloads/tradebook-EI2567_Modified.csv')
    MaxDD = CalcDrawDown(obj.transform_trade_sheet(), 10000)
    MaxDD.draw_down_wealth_index_plot()
    print(MaxDD.draw_down_trade_number, MaxDD.recovery_trade_number)
    print(MaxDD.draw_down_time, MaxDD.recovery_time)







