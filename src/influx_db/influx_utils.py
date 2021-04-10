# %% Main process
"""
I want the ability to test different ideas easily.
Ideas regarding the way we construct the score of stocks
Followed by some visualization of the scores across different stocks

My input:
Set of functions that takes technical params of a stock and output a single score

My mission is to evaluate the functions as set and individually

1. create another DB for meta-params
2. run the script to fill the meta-params-DB per stock:
- number of days recorded
- number of trading days recorded
-
"""
from typing import *
import datetime
import numpy as np
from typing import List

from influxdb import InfluxDBClient

IB_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DB_RESOLUTION = 5  # (minutes)
SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
HOURS_IN_TRADING_DAY = 7.5
HOURS_IN_DAY = 24
FIRST_DATETIME_OF_DATA = datetime.datetime(2021, 2, 10)  # TODO - change back to (2021, 1, 1)
LAST_DATETIME_OF_DATE = datetime.datetime(2021, 2, 16)  # TODO - change back to (2021, 2, 27)
TOTAL_DAYS_OF_DATA = (LAST_DATETIME_OF_DATE - FIRST_DATETIME_OF_DATA).days
STOCK_FIELDS = ['time', 'close', 'volume']


def get_field_indices(fields: List[str]) -> List[int]:
    return [STOCK_FIELDS.index(f) for f in fields]


class InfluxUtils:
    def __init__(self, client):
        self.client = client

    def timestamp_to_datetime(self, time_stamp):
        """
        :param time_stamp: number like 1608674400.0
        :return: object like datetime.datetime(2020, 12, 23)
        """
        return datetime.datetime.fromtimestamp(time_stamp)

    def datetime_to_timestamp(self, date_time):
        """
        :param date_time: object like  datetime.datetime(2020, 12, 23)
        :return: number like 1608674400.0
        """
        return datetime.datetime.timestamp(date_time)

    def db_time_to_timestamp(self, strange_time):
        """
        Gets time point from the database and convert it to float timestamp
        :param strange_time: time to be converted
        :return: time after conversion, days
        """
        return datetime.datetime.strptime(strange_time, IB_DATE_FORMAT).timestamp()

    def get_single_stock_data(self, symbol: str, from_datetime: datetime.datetime, to_datetime: datetime.datetime) -> Optional[List[List[str or int or float]]]:
        """
        Collecting data by 'STOCK_FIELDS' fields on a single stock.
        :param symbol: The stock symbol
        :param from_datetime: TODO The number of days back from now which the data will be collected
        :param to_datetime: TODO The number of days back from now which the data will be collected
        :return: list of series' of data (time and STOCK_FIELDS)
        """
        query_result = self.client.query(
            'SELECT *::field FROM "stock_market"."autogen".' + symbol +
            ' WHERE time > ' + str(int(self.datetime_to_timestamp(from_datetime)) * 10 ** 9) + ' AND time < ' + str(
                int(self.datetime_to_timestamp(to_datetime)) * 10 ** 9))
        if len(query_result.raw['series']) == 0:
            return None
        field_names = query_result.raw['series'][0]['columns']
        field_values = query_result.raw['series'][0]['values']
        ii = np.where(np.array([x in STOCK_FIELDS for x in field_names]))  # all the interesting indices by STOCK_FIELDS
        return [[x[i] for x in field_values] for i in list(*ii)]  # gather fields for all STOCK_FIELD's, for all timestamps

    def get_stock_summary(self, symbol: str) -> Dict:
        """
        Extract some metadata regarding the stock:
        1. total days of data on it
        2. total trading days on it (there are lots of gaps in the stock 24/7 view)
        :param symbol: The stock symbol
        :return: Dictionary of the metadata
        """
        stock_data = self.get_single_stock_data(symbol, FIRST_DATETIME_OF_DATA, LAST_DATETIME_OF_DATE)  # takes approximately 0.2 seconds
        if stock_data is None:
            return {'total_days': 0, 'total_trading_days': 0}
        total_time_on_stock = (self.db_time_to_timestamp(stock_data[0][-1]) - self.db_time_to_timestamp(stock_data[0][0])) // (
                SECONDS_IN_MINUTE * MINUTES_IN_HOUR * HOURS_IN_DAY)
        continuous_time_on_stock = len(stock_data[0]) * DB_RESOLUTION // (MINUTES_IN_HOUR * HOURS_IN_TRADING_DAY)
        return {'symbol': symbol, 'total_days': total_time_on_stock, 'total_trading_days': continuous_time_on_stock}

    def get_all_stocks_data(self, from_datetime: datetime.datetime.timestamp, to_datetime: datetime.datetime.timestamp):
        """
        Getting all data (from FIRST_DATETIME_OF_DATA to LAST_DATETIME_OF_DATA) of all the stocks we have in our DB
        :return: GIGANTIC LIST TODO - what exactly?
        """
        stocks = str(list(map(lambda x: x['name'], self.client.get_list_measurements()))).replace('\'', '').replace(' ', '').replace(']', '').replace('[', '')
        now = datetime.datetime.now().timestamp()
        query_result = self.client.query(
            'SELECT *::FIELD FROM "stock_market"."autogen".' + stocks +
            ' WHERE time > ' + str(int(self.datetime_to_timestamp(from_datetime)) * 10 ** 9) + ' AND time < ' + str(
                int(self.datetime_to_timestamp(to_datetime)) * 10 ** 9))
        print('Data collection of all stocks took: ' + str(datetime.datetime.now().timestamp() - now))
        print('king')


if __name__ == '__main__':
    # client = InfluxDBClient()
    # client.switch_database(client.get_list_database()[1]['name'])
    #
    # influx_utils = InfluxUtils(client)
    # apple_stock_summary = influx_utils.get_stock_summary('AACG')

    # TEMP_DATETIME_OF_DATA = datetime.datetime(2021, 2, 17)
    # get_all_stocks_data(from_datetime=TEMP_DATETIME_OF_DATA, to_datetime=LAST_DATETIME_OF_DATE)
    print('king')

    # working!!
    # stocks = str(list(map(lambda x:x['name'], client.get_list_measurements())))[1:-2].replace('\'', '').replace(' ', '')
    # client.query('SELECT ' + 'close' + ' FROM "stock_market"."autogen".' + stocks + ' WHERE time > now() - 60d')
