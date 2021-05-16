from Data_Wrappers.Indicators.Indicator import Indicator
import pandas_ta as ta

class EMA(Indicator):
    def __init__(self, **kwargs):
        super().__init__()
        self.interval = kwargs.get('interval')
        self.on = kwargs.get('on')

    def cal_indicator(self, **kwargs):
        data = kwargs.get('data')
        try:
            ema = ta.ema(data[self.on], length=self.interval)
        except:
            print('s')
        data['ema' + "_" + str(self.interval)] = ema
        return data