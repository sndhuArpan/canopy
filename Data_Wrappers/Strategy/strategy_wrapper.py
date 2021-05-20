from utils.Utils import Utils as Util
from Data_Wrappers.Angel_Broker.Angel_Broker_Wrapper import Angel_Broker_Wrapper


class strategy_wrapper:
    def __init__(self, **kwargs) -> object:

        share_name = kwargs.get('share_name')
        time_interval_list = kwargs.get('time_interval')
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        broker = kwargs.get('broker')
        indicators = kwargs.get('indicators')
        self.data_list = {}
        if broker == 'angle':
            angle_broker = Angel_Broker_Wrapper()
            for share in share_name:
                print(share)
                share_token = Util.get_symbol_token(share)
                for time_interval in time_interval_list:
                    data = angle_broker.get_symbol_data(share_token, time_interval, start_date=start_date, end_date=end_date)
                    if not indicators is None:
                        for indicator in indicators:
                            data = indicator.cal_indicator(data=data)
                    self.data_list[share + '_' + time_interval.name] = data


    def backtest_strategy(self):
        pass

    def buy_share(self):
        pass

    def sell_share(self):
        pass
