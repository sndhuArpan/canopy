from Data_Wrappers.Indicators.Indicator import Indicator
import pandas_ta as ta

class SMA(Indicator):
    def __init__(self, **kwargs):
        super().__init__()
        self.interval = kwargs.get('interval')
        self.on = kwargs.get('on')

    def cal_indicator(self, **kwargs):
        data = kwargs.get('data')
        sma = ta.sma(data[self.on], length=self.interval)
        data['sma' + "_" + str(self.interval)] = sma
        return data

