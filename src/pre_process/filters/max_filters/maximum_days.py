from typing import *
from abc import abstractmethod

import numpy as np
from src.pre_process.filters.abstract_filter import AbstractFilter


class MaximumDaysFilter(AbstractFilter):

    @abstractmethod
    def get_key(self):
        raise NotImplementedError

    def filter(self) -> List[str]:
        """
        Filtering all stocks in our Database, By the those that have full data from time ranges defined in 'InfluxUtils' class.
        :return: List of strings as the symbols of the stocks
        """
        # get all stocks
        stocks_summary = [self.influxUtils.get_stock_summary(x) for x in list(map(lambda x: x['name'], self.client.get_list_measurements()))]
        stocks_total_days = list(map(lambda x: x[self.get_key()], stocks_summary))

        # get a list of only the stocks with the entire data
        full_data_stocks = np.array([x['symbol'] if x[self.get_key()] == max(stocks_total_days) else 'None' for x in stocks_summary])
        return list(full_data_stocks[full_data_stocks != 'None'])
