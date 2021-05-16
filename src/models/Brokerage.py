class Brokerage:
    broker =  None

    def __init__(self, broker):
        Brokerage.broker = broker

    @staticmethod
    def get_brokerage_charges():
        if Brokerage.broker.upper() == 'Angel'.upper():
            dict_rt = {'eq_del': 0,
                       'eq_intra_min' : 0.0005,
                       'eq_intra_max' : 40,
                       'eq_future_min' : 0.0005,
                       'eq_future_max': 40,
                       'eq_option_per_lot' : 20,
                       'eq_stt' : 0.0001,
                       'eq_stamp_duty': 0.0001,
                       'eq_other' : 0.00005}
            return dict_rt


if __name__ == '__main__':
    print(Brokerage('angel').get_brokerage_charges())