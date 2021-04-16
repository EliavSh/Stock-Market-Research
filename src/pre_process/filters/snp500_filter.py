from typing import *
import pandas as pd

from src.pre_process.filters.abstract_filter import AbstractFilter


class SNP500Filter(AbstractFilter):

    def filter(self) -> List[str]:
        """
        Filtering all stocks in our Database, By the those that have full data from time ranges defined in 'InfluxUtils' class.
        :return: List of strings as the symbols of the stocks
        """
        snp500_stocks = list(pd.read_csv('pre_process/data_utils/constituents.csv')['Symbol'])

        ignored_stocks = ['ALL', 'BRK.B', 'BF.B', 'KEY', 'KEYS']

        for stock in ignored_stocks:
            snp500_stocks.remove(stock)

        return snp500_stocks
