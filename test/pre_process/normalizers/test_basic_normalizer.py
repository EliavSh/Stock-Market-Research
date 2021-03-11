import unittest
import pandas as pd

from src import *
from test import *


class TestBasicNormalizer(unittest.TestCase):

    def setUp(self) -> None:
        self.utils = Utils()
        stock_symbols = list(range(4))
        stock_lengths = [30] * 4
        self.stocks_data = dict(zip(['stock_' + str(i) for i in stock_symbols], [self.utils.generate_stock_data(size) for size in stock_lengths]))
        self.config = MainConfig()
        self.config.prediction_interval = [12]

    def test(self):
        expected = max([max([len(values_list) for values_list in self.stocks_data[symbol]]) for symbol in self.stocks_data]) - 1

        basic_normalizer = NormalizerEnum.BasicNormalizer.get(self.config)
        basic_normalizer.normalize(self.stocks_data)

        # assert that all series's are with the same length (we eliminate the first element of each series while normalizing)
        for value_to_check in range(len(self.utils.stock_fields) - 1):
            unique_length_series = pd.Series([len(self.stocks_data[x][value_to_check]) for x in self.stocks_data.keys()]).unique()
            self.assertEqual(1, len(unique_length_series), 'Should be 1')
            self.assertEqual(expected, unique_length_series[0])
