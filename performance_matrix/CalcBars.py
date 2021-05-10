from math import ceil
from datetime import timedelta
from Util import interval_enum


class CalcBars:

    @staticmethod
    def get_days(start, end):
        return (end - start).days

    @staticmethod
    def get_weeks(start, end):
        monday1 = (start - timedelta(days=start.weekday()))
        monday2 = (end - timedelta(days=end.weekday()))
        return (monday2 - monday1).days / 7

    @staticmethod
    def get_hours(minutes):
        hours = ceil(minutes/60)
        return hours

    @staticmethod
    def get_minutes(start, end):
        timedelta = end - start
        minutes = divmod(timedelta.total_seconds(), 60)
        return minutes[0]

    @staticmethod
    def bars_count(start, end, interval):
        minutes = CalcBars.get_minutes(start, end)
        if interval == interval_enum.ONE_DAY.name:
            return CalcBars.get_days(start, end)
        if interval == interval_enum.ONE_WEEK.name:
            return CalcBars.get_weeks(start, end)
        if interval == interval_enum.ONE_HOUR.name:
            return CalcBars.get_hours(minutes)
        if interval == interval_enum.FIFTEEN_MINUTE.name:
            return minutes/interval_enum.FIFTEEN_MINUTE.value



