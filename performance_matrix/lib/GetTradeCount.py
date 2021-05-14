import numpy as np

class GetTradeCount:

    def __init__(self, trade_sheet):
        self.trade_sheet = trade_sheet

    def trade_count(self, start, end):
        count = 0
        for index, row in self.trade_sheet.iterrows():
            if np.isnan(row['realised_profit']):
                continue
            booked_date = row['booked_date']
            if booked_date >= start and booked_date <= end:
                count = count +1
        return count