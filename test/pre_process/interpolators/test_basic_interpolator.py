import unittest
import pandas as pd

from src import *
from test import *


class TestBasicInterpolator(unittest.TestCase):

    def setUp(self) -> None:
        self.utils = Utils()
        stock_symbols = list(range(4))
        stock_lengths = [30, 25, 30, 37]
        self.stocks_data = dict(zip(['stock_' + str(i) for i in stock_symbols], [self.utils.generate_stock_data(size) for size in stock_lengths]))

    def test_all_stocks_lists_lengths_should_be_the_same_as_max_series_length(self):
        basic_interpolation = InterpolationEnum.BasicInterpolation.get()
        basic_interpolation.interpolate(stocks_data=self.stocks_data)

        # assert the length of each list equals the length of the maximum series
        for value_to_check in range(len(self.utils.stock_fields) - 1):
            unique_length_series = pd.Series([len(self.stocks_data[x][value_to_check]) for x in self.stocks_data.keys()]).unique()
            self.assertEqual(1, len(unique_length_series), 'Should be 1')
            self.assertEqual(max([max([len(values_list) for values_list in self.stocks_data[symbol]]) for symbol in self.stocks_data]), unique_length_series[0])

        time_length_series = pd.Series([len(self.stocks_data[x][0]) for x in self.stocks_data.keys()])
        print('Description of number of timestamps for our stocks after interpolation:\n' + str(time_length_series.describe()) + '\n')


if __name__ == '__main__':
    unittest.main()
