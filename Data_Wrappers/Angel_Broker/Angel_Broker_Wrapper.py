from Data_Wrappers.Abstract_Provider.Data_Wrapper_Abstract import Data_Wrapper
from smartapi import SmartConnect
import enum
from datetime import datetime, timedelta
import pandas as pd
from Util import Util, interval_enum
import time
import requests as request
import csv
import os
from dateutil.relativedelta import relativedelta


class max_days(enum.Enum):
    ONE_MINUTE = 25
    THREE_MINUTE = 80
    FIVE_MINUTE = 80
    TEN_MINUTE = 80
    FIFTEEN_MINUTE = 150
    THIRTY_MINUTE = 150
    ONE_HOUR = 350
    ONE_DAY = 1800


class Angel_Broker_Wrapper(Data_Wrapper):
    def __init__(self):
        self.connect = SmartConnect(api_key="RTebKHaN")
        self.connect.generateSession("S705342", "poiuhbnm@2")
        super().__init__()

    def get_data(self, data, interval, start_date, end_date):
        df_date = data['datetime'][data.index[-1]]
        start_date = Util.get_hour_start_date(start_date,interval)
        end_date = Util.get_hour_end_date(end_date,interval)
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")

        empty = True
        while empty:
            idx = data.index[data['datetime'] == end_date]
            if idx.empty:
                if not end_date>df_date:
                     end_date = (datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S") + timedelta(days=1)).strftime(
                        "%Y-%m-%dT%H:%M:%S")
                else:
                    end_date = (datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S") - timedelta(days=1)).strftime(
                        "%Y-%m-%dT%H:%M:%S")
            else:
                end_idx = idx[0]
                break
        while empty:
            idx = data.index[data['datetime'] == start_date]
            if idx.empty:
                start_date = (datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S") + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M:%S")
            else:
                start_idx = idx[0]
                break
        return data[start_idx:end_idx + 1]

    def get_symbol_data(self, symboltoken, interval, **kwargs):
        symboltoken = str(symboltoken)
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        file_path = 'historical_data' + '/' + symboltoken + '_' + interval.name
        if not os.path.exists(file_path + '.csv'):
            data = self.save_data(symboltoken, interval, start_date=datetime.today() - relativedelta(years=10),
                                  end_date=datetime.today(), new_data=True)
            return self.get_data(data, interval, start_date, end_date)
        else:
            data = Util.read_csv_df(file_path)
            if not interval == interval_enum.ONE_WEEK or interval == interval_enum.ONE_MONTH:
                last_date = datetime.strptime(data['datetime'][data.index[-1]], "%Y-%m-%dT%H:%M:%S")
            else:
                last_date = datetime.strptime(data['datetime'][data.index[-1]-1], "%Y-%m-%dT%H:%M:%S")
            if last_date < end_date:
                if not interval == interval_enum.ONE_WEEK or interval == interval_enum.ONE_MONTH:
                    data = self.save_data(symboltoken, interval, start_date=last_date + timedelta(days=1),
                                          end_date=datetime.today(), new_data=False)
                else:
                    data = self.save_data(symboltoken, interval, start_date=last_date,
                                          end_date=datetime.today(), new_data=False)
            return self.get_data(data, interval, start_date, end_date)

    def save_data(self, symboltoken, interval, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        days = (end_date - start_date).days
        if interval == interval_enum.ONE_WEEK or interval == interval_enum.ONE_MONTH:
            max_day = max_days.__getitem__(interval_enum.ONE_DAY.name).value
        else:
            max_day = max_days.__getitem__(interval.name).value
        loop = True
        df = Util.get_angle_data_df()
        remaining_days = days
        fetched_date = None
        while loop:
            if max_day > days:
                to_date = Util.get_ist_to_date(end_date)
                from_date = Util.get_ist_from_date(start_date)
                loop = False
            else:
                if fetched_date is None:
                    from_date = Util.get_ist_from_date(start_date)
                    to_date = Util.get_ist_to_date((from_date + timedelta(days=max_day)))
                    remaining_days = remaining_days - max_day
                else:
                    fetched_date = Util.convert_str_date(fetched_date)
                    from_date = Util.get_ist_from_date((fetched_date + timedelta(days=1)))
                    if remaining_days < max_day:
                        to_date = Util.get_ist_to_date(end_date)
                        remaining_days = remaining_days - remaining_days
                    else:
                        to_date = Util.get_ist_to_date((fetched_date + timedelta(days=max_day)))
                        remaining_days = remaining_days - max_day
                if remaining_days <= 0:
                    loop = False
            try:
                historicParam = {
                    "exchange": "NSE",
                    "symboltoken": symboltoken,
                    "interval": self.get_valid_interval(interval).name,
                    "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                    "todate": to_date.strftime("%Y-%m-%d %H:%M")
                }
                for i in range(3):
                    data = self.connect.getCandleData(historicParam).__getitem__("data")
                    data_df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                    if not data_df.empty:
                        df = pd.concat([df, data_df],ignore_index = True)
                        fetched_date = historicParam['todate']
                        break
                    else:
                        time.sleep(0.5)
                if i == 2:
                    fetched_date = historicParam['todate']

            except Exception as e:
                print("Historic Api failed: {}".format(e))
                loop = False

        if interval == interval_enum.ONE_WEEK:
            df = self.convert_datetime_day(df)
            df = self.convert_df_weekly(df)
        else:
            if interval == interval_enum.ONE_MONTH:
                df = self.convert_df_montly(df)

        df['datetime'] = [x.split('+')[0] for x in df['datetime']]
        if not kwargs.get('new_data'):
            data = Util.read_csv_df('historical_data/' + symboltoken + '_' + interval.name)
            if not interval == interval_enum.ONE_WEEK or interval == interval_enum.ONE_MONTH:
                df = data.append(df, ignore_index=True)
            else:
                data.drop(data.tail(2).index, inplace=True)
                df = data.append(df, ignore_index=True)

        Util.convert_dataframe_csv(df, 'historical_data',
                                   symboltoken + '_' + interval.name)
        return df

    def get_symbol(self):
        r = request.get("https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json")
        data = r.json()
        keys = data[0].keys()
        a_file = open("symbol.csv", "w")
        dict_writer = csv.DictWriter(a_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
        a_file.close()
        print("done")

    def convert_datetime_day(self, df):
        days = []
        days_dict = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        for date in df['datetime']:
            day = datetime.strptime(date.split("T")[0], "%Y-%m-%d").strftime('%A')
            days.append(days_dict.get(day))

        df['days'] = days
        return df

    def convert_df_weekly(self, df):
        weekly_df = Util.get_angle_data_df()
        start = False
        open = 0.0
        low = 0.0
        close = 0.0
        high = 0.0
        volume = 0.0
        current_day = 0
        week_start_date = ''
        for ind in df.index:
            if start == False:
                start = True
                open = df['open'][ind]
                low = df['low'][ind]
                close = df['close'][ind]
                high = df['high'][ind]
                week_start_date = df['datetime'][ind]
                volume = df['volume'][ind]
            else:
                if df['days'][ind] > current_day:
                    if df['low'][ind] < low:
                        low = df['low'][ind]
                    if high < df['high'][ind]:
                        high = df['high'][ind]
                    volume = volume + df['volume'][ind]
                    current_day = df['days'][ind]
                else:
                    close = df['close'][ind - 1]
                    week_temp_df = {'datetime': week_start_date, 'open': open, 'high': high, 'low': low,
                                    'close': close, 'volume': volume}
                    weekly_df = weekly_df.append(week_temp_df, ignore_index=True)
                    open = df['open'][ind]
                    low = df['low'][ind]
                    close = df['close'][ind]
                    high = df['high'][ind]
                    current_day = df['days'][ind]
                    week_start_date = df['datetime'][ind]
                    volume = df['volume'][ind]

        week_temp_df = {'datetime': week_start_date, 'open': open, 'high': high, 'low': low,
                        'close': df['close'][ind], 'volume': volume}
        if week_temp_df['datetime'] != weekly_df['datetime'][weekly_df.index[-1]]:
            weekly_df = weekly_df.append(week_temp_df, ignore_index=True)
        return weekly_df

    def convert_df_montly(self, df):
        montly_df = Util.get_angle_data_df()
        open = 0.0
        low = 0.0
        close = 0.0
        high = 0.0
        volume = 0.0
        current_month = 0
        month_start_date = ''
        for ind in df.index:
            date = datetime.strptime(df['datetime'][ind].split("T")[0], "%Y-%m-%d")
            month = date.month
            if ind == 0:
                current_month = month
                open = df['open'][ind]
                low = df['low'][ind]
                close = df['close'][ind]
                high = df['high'][ind]
                month_start_date = df['datetime'][ind]
                volume = df['volume'][ind]
            else:
                if current_month == month:
                    if df['low'][ind] < low:
                        low = df['low'][ind]
                    if high < df['high'][ind]:
                        high = df['high'][ind]
                    volume = volume + df['volume'][ind]
                else:
                    close = df['close'][ind - 1]
                    month_temp_df = {'datetime': month_start_date, 'open': open, 'high': high, 'low': low,
                                     'close': close, 'volume': volume}
                    montly_df = montly_df.append(month_temp_df, ignore_index=True)
                    open = df['open'][ind]
                    low = df['low'][ind]
                    close = df['close'][ind]
                    high = df['high'][ind]
                    current_month = month
                    month_start_date = df['datetime'][ind]
                    volume = df['volume'][ind]

        month_temp_df = {'datetime': month_start_date, 'open': open, 'high': high, 'low': low,
                         'close': df['close'][ind], 'volume': volume}
        if datetime.strptime(month_temp_df['datetime'].split("T")[0], "%Y-%m-%d").month != datetime.strptime(
                montly_df['datetime'][montly_df.index[-1]].split("T")[0], "%Y-%m-%d").month:
            montly_df = montly_df.append(month_temp_df, ignore_index=True)
        return montly_df

    def get_valid_interval(self, time_interval):
        if time_interval == interval_enum.ONE_WEEK or time_interval == interval_enum.ONE_MONTH:
            return interval_enum.ONE_DAY
        else:
            return time_interval
