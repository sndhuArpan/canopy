import numpy as np
from datetime import timedelta
from utils.Utils import Utils
from utils.Utils import interval_enum


class CalcBars:

    @staticmethod
    def get_days(start, end):
        return np.busday_count(Utils.get_date_from_timestamp(start), Utils.get_date_from_timestamp(end))

    @staticmethod
    def get_weeks(start, end):
        monday1 = (start - timedelta(days=start.weekday()))
        monday2 = (end - timedelta(days=end.weekday()))
        return (monday2 - monday1).days / 7

    @staticmethod
    def get_hours(start, end, interval):
        no_of_days = np.busday_count(Utils.get_date_from_timestamp(start), Utils.get_date_from_timestamp(end))
        hours = no_of_days * Utils.get_candles_per_day(interval_enum.__getitem__(interval))
        return hours

    @staticmethod
    def get_minutes(start, end):
        #get_hours = CalcBars.get_hours(start, end)
        #minutes = ((start - end).seconds)/60
        timedelta = end - start
        minutes = divmod(timedelta.total_seconds(), 60)
        return minutes[0]


    @staticmethod
    def bars_count(start, end, interval):
        hours = CalcBars.get_hours(start, end, interval_enum.ONE_HOUR.name)
        if interval == interval_enum.ONE_DAY.name:
            return CalcBars.get_days(start, end)
        if interval == interval_enum.ONE_WEEK.name:
            return CalcBars.get_weeks(start, end)
        if interval == interval_enum.ONE_HOUR.name:
            return CalcBars.get_hours(start, end, interval_enum.ONE_HOUR.name)
        if interval == interval_enum.FIFTEEN_MINUTE.name:
            return CalcBars.get_minutes(start, end)/interval_enum.FIFTEEN_MINUTE.value



