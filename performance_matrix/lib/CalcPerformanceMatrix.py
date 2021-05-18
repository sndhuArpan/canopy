import numpy as np
from dateutil.relativedelta import relativedelta

from performance_matrix.lib.CalcDrawDown import CalcDrawDown
from performance_matrix.lib.CalcBars import CalcBars
from performance_matrix.lib.AccountUtilization import AccountUtilization
from performance_matrix.lib.MonteCarloSimulation import MonteCarlosSimulation
from performance_matrix.lib.EquityCurve import EquityCurve
from fractions import Fraction
import shutil
import os
import pandas as pd


class CalcPerformanceMatrix:

    def __init__(self, transformed_trade_sheet_path, initial_account_value, ruin_equity, volatility_period=30):
        self.trade_df = pd.read_csv(transformed_trade_sheet_path)
        self.base_dir = os.path.dirname(transformed_trade_sheet_path)
        self.plot_dir = os.path.join(os.path.dirname(transformed_trade_sheet_path), 'img')
        self._create_css_and_img_folder()
        self._convert_df_datetime()
        self.initial_account_value = initial_account_value
        self.ruin_equity = ruin_equity
        self.volatility_period = volatility_period
        self.AccountUtilization_obj = AccountUtilization(self.trade_df, self.initial_account_value, self.plot_dir)
        self.EquityCurve_obj = EquityCurve(self.trade_df, self.initial_account_value, self.volatility_period, self.plot_dir)
        self.CalcDrawDown_obj = CalcDrawDown(self.trade_df, self.initial_account_value, self.plot_dir)

    def _create_css_and_img_folder(self):
        to_path = self.base_dir
        from_path = '/Users/Sandhu/canopy/canopy/performance_matrix/lib/src_html'
        shutil.copytree(from_path, to_path, dirs_exist_ok=True)

    def _convert_df_datetime(self):
        self.trade_df['entry_datetime'] = self.trade_df['entry_datetime'].astype('datetime64[ns]')
        self.trade_df['exit_datetime'] = self.trade_df['exit_datetime'].astype('datetime64[ns]')
        self.trade_df['booked_date'] = self.trade_df['booked_date'].astype('datetime64[ns]')

    @staticmethod
    def _value_change(initial_value, percentage):
        return (initial_value * percentage)/100

    def net_profit(self):
        return int(self.trade_df['realised_profit'].sum())

    def profit_factor(self):
        profit_value = self.trade_df.loc[self.trade_df['realised_profit'] > 0, 'realised_profit'].sum()
        loss_value = self.trade_df.loc[self.trade_df['realised_profit'] < 0, 'realised_profit'].sum()
        profit_factor = profit_value / abs(loss_value)
        return str(Fraction(profit_factor).limit_denominator(100))

    def total_no_trade(self):
        null_trades = self.trade_df['realised_profit'].isna().sum()
        total_trade = self.trade_df['system_trade_id'].count() - null_trades
        return total_trade

    def win_rate(self):
        total_winners = self.trade_df.loc[self.trade_df['realised_profit'] > 0, 'realised_profit'].count()
        total_losers = self.trade_df.loc[self.trade_df['realised_profit'] < 0, 'realised_profit'].count()
        win_rate = round(total_winners/total_losers, 2)
        return str(Fraction(win_rate).limit_denominator(10))

    def average_win(self):
        total_winners = self.trade_df.loc[self.trade_df['realised_profit'] > 0, 'realised_profit'].count()
        profit_value = self.trade_df.loc[self.trade_df['realised_profit'] > 0, 'realised_profit'].sum()
        return int(profit_value/total_winners)

    def maximum_profit_per_trade(self):
        max_profit = self.trade_df.loc[self.trade_df['realised_profit'] > 0, 'realised_profit'].max()
        return int(max_profit)

    def maximum_loss_per_trade(self):
        max_loss = self.trade_df.loc[self.trade_df['realised_profit'] < 0, 'realised_profit'].min()
        return int(max_loss)

    def average_loss(self):
        loss_value = self.trade_df.loc[self.trade_df['realised_profit'] < 0, 'realised_profit'].sum()
        total_losers = self.trade_df.loc[self.trade_df['realised_profit'] < 0, 'realised_profit'].count()
        return int(loss_value/total_losers)

    def trade_charges(self):
        return int(self.trade_df['trade_charges'].sum())

    def risk_reward_ratio(self):
        count = 0
        ratio = 0
        for index, row in self.trade_df.iterrows():
            if row['risk_reward_ratio'] >= 0:
                ratio = ratio + row['risk_reward_ratio']
                count = count + 1
        return str(Fraction(ratio/count).limit_denominator(100))

    def drawdown_matrix(self):
        dd_dict = {'maximum_drawdown': round(self.CalcDrawDown_obj.maximum_drawdown,2),
                   'max_drawdown_date': self.CalcDrawDown_obj.max_drawdown_date,
                   'draw_down_start_time': self.CalcDrawDown_obj.draw_down_start_time,
                   'draw_down_time': self.CalcDrawDown_obj.draw_down_time,
                   'draw_down_trade_number': self.CalcDrawDown_obj.draw_down_trade_number,
                   'recovery_date': self.CalcDrawDown_obj.draw_down_end_time,
                   'recovery_time': self.CalcDrawDown_obj.recovery_time,
                   'recovery_trade_number': self.CalcDrawDown_obj.recovery_trade_number}
        return dd_dict

    def drawdown_matrix_plot(self):
        return self.CalcDrawDown_obj.draw_down_wealth_index_plot()

    def bars_held(self):
        total_bars = 0
        total_trades = 0
        maximum_bars = 0
        minimum_bars = 0
        for index, row in self.trade_df.iterrows():
            if np.isnan(row['realised_profit']):
                continue
            bars = CalcBars.bars_count(row['entry_datetime'], row['booked_date'], row['interval'])
            if bars is None:
                bars = 0
            total_bars = total_bars + bars
            total_trades = total_trades + 1
            if bars >= maximum_bars:
                maximum_bars = bars
            if bars <= minimum_bars:
                minimum_bars = bars
        bars_held_dict = {'average_bars': round(total_bars/total_trades,2),
                          'maximum_bars': maximum_bars,
                          'minimum_bars': minimum_bars}
        return bars_held_dict

    def max_account_utilized(self):
        utilization_dict =  self.AccountUtilization_obj.account_utilization_matrix()
        return utilization_dict

    def account_uitlization_plot(self):
        return self.AccountUtilization_obj.plot_graph()

    def calmar_ratio(self):
        cagr = self.cagr()
        dd = self.drawdown_matrix().get('maximum_drawdown')
        return round(abs(cagr/dd), 2)

    def sharpe_ratio(self, rf=0.05):
        returns = self.EquityCurve_obj.wealth_and_profit_df['log_Ret']
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (returns.mean() - rf) / volatility
        return round(sharpe_ratio,2)

    def cagr(self):
        end_date = self.EquityCurve_obj.wealth_and_profit_df['booked_date'].max()
        start_date = self.EquityCurve_obj.wealth_and_profit_df['booked_date'].min()
        period = relativedelta(end_date, start_date).years
        if period == 0:
            return None
        else:
            account_final_value = self.EquityCurve_obj.wealth_and_profit_df.iloc[-1]['wealth']
            cagr_rt = (account_final_value / self.initial_account_value) ** (1/period) - 1
            return round(cagr_rt*100, 2)

    def equity_curve(self):
        dict_rt = {}
        dict_rt['Equity_Wealth_Curve_Plot'] = self.EquityCurve_obj.generate_equity_wealth_curve()
        dict_rt['Equity_Profit_Plot'] = self.EquityCurve_obj.generate_equity_profit_curve()
        dict_rt['Volatility_Return_Plot'] = self.EquityCurve_obj.generate_volatility_return_graph()
        return dict_rt

    def monte_carlo_simulation(self):
        profit_list = self.EquityCurve_obj.wealth_and_profit_df['profit']
        start_equity = self.initial_account_value
        ruin_equity = self.ruin_equity
        obj = MonteCarlosSimulation(profit_list, start_equity, ruin_equity, self.plot_dir)
        return obj.save_image()
