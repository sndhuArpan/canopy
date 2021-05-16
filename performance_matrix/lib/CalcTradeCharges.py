from src.models.Brokerage import Brokerage
from utils.Utils import Utils


class CalcTradeCharges:

    def __init__(self, broker, instrument_type, start_time, buy_value,
                 buy_quantity, exit_time, sell_value, sell_quantity):
        self.broker = broker
        self.instrument_type = instrument_type
        self.start_time = start_time
        self.buy_value = buy_value
        self.buy_quantity = buy_quantity
        self.exit_time = exit_time
        self.sell_value = sell_value
        self.sell_quantity = sell_quantity
        self.brokerage_dict = Brokerage(broker).get_brokerage_charges()
        self.charges =  self.get_charges()

    def get_charges(self):
        brokerage_plus_gst = self.get_brokerage_plus_gst()
        stt = self.get_stt()
        stampduty_other_charges = self.get_stampduty_and_other_charges()
        return  brokerage_plus_gst + stt + stampduty_other_charges

    def get_brokerage_plus_gst(self):
        if self.instrument_type.upper() == 'Equity'.upper():
            no_of_days = Utils.get_no_of_days_between_dates(self.start_time, self.exit_time)
            if no_of_days <= 3:
                eq_intra_min = self.brokerage_dict.get('eq_intra_min')
                eq_intra_max = self.brokerage_dict.get('eq_intra_max')
                brokerage_max = (self.buy_value + self.sell_value) * eq_intra_min
                if brokerage_max > eq_intra_max:
                    eq_intra_max = eq_intra_max + (eq_intra_max*.18)
                    return eq_intra_max
                else:
                    brokerage_max = brokerage_max + (brokerage_max * .18)
                    return brokerage_max
            else:
                return 0

    def get_stt(self):
        if self.instrument_type.upper() == 'Equity'.upper():
            stt_charge_percentage = self.brokerage_dict.get('eq_stt')
            trade_value = self.buy_value + self.sell_value
            stt = trade_value * stt_charge_percentage
            return stt

    def get_stampduty_and_other_charges(self):
        if self.instrument_type.upper() == 'Equity'.upper():
            stamp_duty_charge_percentage = self.brokerage_dict.get('eq_stamp_duty')
            other_charge_percentage = self.brokerage_dict.get('eq_other')
            trade_value = self.buy_value + self.sell_value
            total = (trade_value * stamp_duty_charge_percentage) + (other_charge_percentage * trade_value)
            return total

