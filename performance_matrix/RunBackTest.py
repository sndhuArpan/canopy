import os
import webbrowser
from pathlib import Path
from performance_matrix.lib.CalcPerformanceMatrix import CalcPerformanceMatrix
from performance_matrix.lib.TransfromTradeSheet import TransformTradeSheet
from performance_matrix.lib.RenderHTML import RenderHTML


def run_backtest(report_file, run_type ,initial_amount_value, ruin_equity, monte_carlo):
    backtest_report_dict = {}
    # transforming trade sheet
    print('Transforming Trade sheet')
    obj = TransformTradeSheet(report_file, run_type)
    trade_sheet = obj.transform_trade_sheet()
    print('Create Calculation Matrix Objects')
    Calc_Obj = CalcPerformanceMatrix(trade_sheet, initial_amount_value, ruin_equity)
    print('Get Basic Values')
    backtest_report_dict['Report_Name'] = os.path.splitext(os.path.basename(report_file))[0] + ' - ' + run_type
    backtest_report_dict['Net_Profit'] = Calc_Obj.net_profit()
    backtest_report_dict['net_charges'] = Calc_Obj.trade_charges()
    backtest_report_dict['profit_factor'] = Calc_Obj.profit_factor()
    backtest_report_dict['total_no_trade'] = Calc_Obj.total_no_trade()
    backtest_report_dict['win_rate'] = Calc_Obj.win_rate()
    backtest_report_dict['average_win'] = Calc_Obj.average_win()
    backtest_report_dict['average_loss'] = Calc_Obj.average_loss()
    backtest_report_dict['maximum_profit'] = Calc_Obj.maximum_profit_per_trade()
    backtest_report_dict['maximum_loss'] = Calc_Obj.maximum_loss_per_trade()
    backtest_report_dict['risk_reward_ratio'] = Calc_Obj.risk_reward_ratio()
    backtest_report_dict['sharpe_ratio'] = Calc_Obj.sharpe_ratio()
    backtest_report_dict['cagr'] = Calc_Obj.cagr()
    backtest_report_dict['calmar_ratio'] = Calc_Obj.calmar_ratio()
    print('Get Bars Held Values')
    backtest_report_dict['average_bars'] = Calc_Obj.bars_held().get('average_bars')
    backtest_report_dict['maximum_bars'] = Calc_Obj.bars_held().get('maximum_bars')
    backtest_report_dict['minimum_bars'] = Calc_Obj.bars_held().get('minimum_bars')
    print('Get Drawdown Value')
    backtest_report_dict['maximum_drawdown'] = Calc_Obj.drawdown_matrix().get('maximum_drawdown')
    backtest_report_dict['max_drawdown_date'] = Calc_Obj.drawdown_matrix().get('max_drawdown_date')
    backtest_report_dict['draw_down_start_time'] = Calc_Obj.drawdown_matrix().get('draw_down_start_time')
    backtest_report_dict['draw_down_time'] = Calc_Obj.drawdown_matrix().get('draw_down_time')
    backtest_report_dict['draw_down_trade_number'] = Calc_Obj.drawdown_matrix().get('draw_down_trade_number')
    backtest_report_dict['recovery_date'] = Calc_Obj.drawdown_matrix().get('recovery_date')
    backtest_report_dict['recovery_time'] = Calc_Obj.drawdown_matrix().get('recovery_time')
    backtest_report_dict['recovery_trade_number'] = Calc_Obj.drawdown_matrix().get('recovery_trade_number')
    backtest_report_dict['Drawdown_Plot'] = Path(Calc_Obj.drawdown_matrix_plot()).name
    print('Get Account Utilization')
    backtest_report_dict['max_amount_utilized_percentage'] = Calc_Obj.max_account_utilized().get('max_amount_utilized_percentage')
    backtest_report_dict['min_amount_utilized_percentage'] = Calc_Obj.max_account_utilized().get('min_amount_utilized_percentage')
    backtest_report_dict['average_amount_utilized_percentage'] = Calc_Obj.max_account_utilized().get('average_amount_utilized_percentage')
    backtest_report_dict['max_trades_active'] = Calc_Obj.max_account_utilized().get('max_trades_active')
    backtest_report_dict['min_trades_active'] = Calc_Obj.max_account_utilized().get('min_trades_active')
    backtest_report_dict['average_trades_active'] = Calc_Obj.max_account_utilized().get('average_trades_active')
    backtest_report_dict['Account_Utilization_Plot'] = Path(Calc_Obj.account_uitlization_plot()).name
    print('Get Equity Curve')
    backtest_report_dict['Equity_Wealth_Curve_Plot'] = Path(Calc_Obj.equity_curve().get('Equity_Wealth_Curve_Plot')).name
    backtest_report_dict['Equity_Profit_Plot'] = Path(Calc_Obj.equity_curve().get('Equity_Profit_Plot')).name
    backtest_report_dict['Volatility_Return_Plot'] = Path(Calc_Obj.equity_curve().get('Volatility_Return_Plot')).name
    if monte_carlo:
        print('Running Monte Carlo Simulation ')
        backtest_report_dict['Monte_Carlo_Plot'] = Path(Calc_Obj.monte_carlo_simulation()).name
    backtest_report_dict['base_dir'] = Calc_Obj.base_dir
    return backtest_report_dict

def render_html(backtext_result):
    Render_Obj = RenderHTML('index.html', backtext_result)
    base_dir = backtext_result.get('base_dir')
    new_html_file = os.path.join(base_dir, 'backtest_report.html')
    Render_Obj.generate_new_file(new_html_file)
    return new_html_file


if __name__ == '__main__':
    report_file = '/Users/Sandhu/Downloads/IntraRangeBreak-1.csv'
    run_type = 'Buy_sell_both_run'
    initial_amount_value = 100000
    ruin_equity = 70000
    volatity = 30
    monte_carlo = True
    backtest_result = run_backtest(report_file, run_type, initial_amount_value, ruin_equity, monte_carlo)
    #print(backtest_result)
    file_name = render_html(backtest_result)
    webbrowser.open('file://' + file_name)

# import pdfkit
#
# wkhtmltopdf_options = {
#     'enable-local-file-access': None
# }
#
# pdfkit.from_file('backtest_report.html', 'sample.pdf', options = wkhtmltopdf_options)