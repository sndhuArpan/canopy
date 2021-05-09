from performance_matrix.CalcPerformanceMatrix import CalcPerformanceMatrix
from performance_matrix.TransfromTradeSheet import TransformTradeSheet


def run_backtest(report_file ,initial_amount_value ,ruin_equity, monte_carlo):
    backtest_report_dict = {}
    # transforming trade sheet
    print('Transforming Trade sheet')
    obj = TransformTradeSheet(report_file)
    trade_sheet = obj.transform_trade_sheet()
    print('Create Calculation Matrix Objects')
    Calc_Obj = CalcPerformanceMatrix(trade_sheet, initial_amount_value, ruin_equity)
    print('Get Basic Values')
    backtest_report_dict['Net_Profit'] = Calc_Obj.net_profit()
    backtest_report_dict['profit_factor'] = Calc_Obj.profit_factor()
    backtest_report_dict['total_no_trade'] = Calc_Obj.total_no_trade()
    backtest_report_dict['win_rate'] = Calc_Obj.win_rate()
    backtest_report_dict['average_win'] = Calc_Obj.average_win()
    backtest_report_dict['average_loss'] = Calc_Obj.average_loss()
    backtest_report_dict['risk_reward_ratio'] = Calc_Obj.risk_reward_ratio()
    backtest_report_dict['sharpe_ratio'] = Calc_Obj.sharpe_ratio()
    backtest_report_dict['cagr'] = Calc_Obj.cagr()
    backtest_report_dict['calmar_ratio'] = Calc_Obj.calmar_ratio()
    print('Get Bars Held Values')
    backtest_report_dict['bars_held_dict'] = Calc_Obj.bars_held()
    print('Get Drawdown Value')
    backtest_report_dict['drawdown_matrix'] = Calc_Obj.drawdown_matrix()
    print('Get Account Utilization')
    backtest_report_dict['Account_utilization'] = Calc_Obj.max_account_utilized()
    print('Get Equity Curve')
    Calc_Obj.equity_curve()
    print(backtest_report_dict)
    if monte_carlo:
        print('Running Monte Carlo Simulation :')
        Calc_Obj.monte_carlo_simulation()


if __name__ == '__main__':
    report_file = '/Users/Sandhu/Downloads/APOLLOHOSP-EQ_ONE_DAY.csv'
    initial_amount_value = 200000
    ruin_equity = 150000
    volatity = 30
    monte_carlo = True
    run_backtest(report_file, initial_amount_value, ruin_equity, monte_carlo)