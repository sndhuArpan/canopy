import random
import pandas as pd
import warnings

desired_width = 320
pd.set_option('display.width', desired_width)

from performance_matrix.lib.matrix_charts.PlotBasicTableFromDF import PlotBasicTableFromDF

class MonteCarlosSimulation:

    def __init__(self, profit_list, start_equity, ruin_equity, simulation=2500, lot_size=1):
        self.profit_list = profit_list
        self.startequity = start_equity
        self.margin = ruin_equity
        self.lotsize = lot_size
        self.equityincrement = int(self.startequity / 4)
        self.trades = len(self.profit_list)
        self.niters = simulation

    @staticmethod
    def return_by_dd(drawdown, equity, C1):
        if drawdown != 0:
            return ((equity/C1)-1)/drawdown

    def simulator(self):
        df_main = pd.DataFrame(columns=['Start_Equity', 'Ruin', 'Median_Drawdown_%', 'Median_Equity', 'Median_return_%', 'Return_by_DD'])
        end_equity = int(self.startequity + 11*self.equityincrement)
        for C1 in range(self.startequity, end_equity, self.equityincrement):
            Beginequity = C1
            totalriskofriun =0
            for Iteration in range(1, self.niters):
                equity = Beginequity
                drawdown = 0
                maxequity = equity
                ruin = 0
                df = pd.DataFrame(columns=['equity', 'drawdown', 'rate_of_return', 'return_by_dd'])
                for itrades in range(1, self.trades):
                    tradevalue = random.choice(self.profit_list)
                    ncontracts = self.lotsize
                    if equity < self.margin:
                        ncontracts = 0
                        ruin = 1
                    equity = equity + ncontracts * tradevalue
                    if equity > maxequity:
                        maxequity = equity
                    else:
                        dd = 1 - (equity / maxequity)
                        if dd > drawdown:
                            drawdown = dd
                totalriskofriun = totalriskofriun + ruin
                dict_append = {'equity': equity,
                               'drawdown': drawdown,
                               'rate_of_return': ((equity/C1) -1),
                               'return_by_dd':MonteCarlosSimulation.return_by_dd(drawdown,equity,C1)}
                df = df.append(dict_append, ignore_index=True)
            totalriskofriun = (totalriskofriun/self.niters)*100
            dict_main_append = {'Start_Equity': C1,
                                'Ruin': totalriskofriun,
                                'Median_Drawdown_%': round(df['drawdown'].median() * 100, 2),
                                'Median_Equity': df['equity'].median(),
                                'Median_return_%': round(df['rate_of_return'].median() * 100,2),
                                'Return_by_DD': round(df['return_by_dd'].median(),2)}
            df_main = df_main.append(dict_main_append, ignore_index=True)
        return df_main

    def save_image(self):
        plot_dict = {'plot_df': self.simulator(),
                     'image_file': 'MonteCarloSimiulation'
                     }
        plot_obj = PlotBasicTableFromDF(**plot_dict)
        plot_obj.get_image()


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        profit_list = random.sample(range(-650, 600), 200)
        startequity = 20000
        margin = 16000
        lotsize = 1
        obj = MonteCarlosSimulation(profit_list, startequity, margin, 10)
        obj.save_image()

