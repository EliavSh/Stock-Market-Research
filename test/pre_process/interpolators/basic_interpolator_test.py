import unittest
import datetime
from typing import List, Union
import pandas as pd

from src import *

IB_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
STOCK_FIELDS = ['time', 'close', 'high', 'low', 'open', 'volume']


def generate_datetime_points(size: int) -> List[str]:
    datetime_list = []
    for i in range(size):
        datetime_list.append(datetime.datetime.fromtimestamp(1000 * i).strftime(IB_DATE_FORMAT))

    return datetime_list


def generate_stock_data(size: int) -> List[Union[List[str], List[int], List[float]]]:
    """
    Creating stocks_data from 'size' of datetime points and 'range(size)' values for close, high, low, open and volume
    """
    return [generate_datetime_points(size), *[list(range(size)) for _ in range(len(STOCK_FIELDS) - 1)]]


class BasicInterpolatorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.stocks_data = {'stock_1': generate_stock_data(30), 'stock_2': generate_stock_data(25), 'stock_3': generate_stock_data(30),
                            'stock_4': generate_stock_data(37)}

    def test(self):
        basic_interpolation = InterpolationEnum.BasicInterpolation.get()
        interpolated_data = basic_interpolation.interpolate(stocks_data=self.stocks_data)

        # assert the length of each list equals the length of the maximum series
        for value_to_check in range(len(STOCK_FIELDS) - 1):
            unique_length_series = pd.Series([len(interpolated_data[x][value_to_check]) for x in interpolated_data.keys()]).unique()
            self.assertEqual(len(unique_length_series), 1, 'Should be 1')
            self.assertEqual(unique_length_series[0], max([max([len(values_list) for values_list in interpolated_data[symbol]]) for symbol in interpolated_data]))

        time_length_series = pd.Series([len(interpolated_data[x][0]) for x in interpolated_data.keys()])
        print('Description of number of timestamps for our stocks after interpolation:\n' + str(time_length_series.describe()) + '\n')

