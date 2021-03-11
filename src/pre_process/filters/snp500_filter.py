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

        # get all stocks
        # stocks_summary = [self.influxUtils.get_stock_summary(x) if x not in ignored_stocks else None for x in list(stocks_info['Symbol'].values)]
        # stocks_summary = list(filter(None, stocks_summary))
        # stocks_total_days = list(map(lambda x: x['total_days'], stocks_summary))
        # stocks_trading_days = list(map(lambda x: x['total_trading_days'], stocks_summary))

        # get a list of only the stocks with the entire data
        # full_data_stocks_total_days = np.array([x['symbol'] if x['total_days'] == max(stocks_total_days) else 'None' for x in stocks_summary])
        # full_data_stocks_total_days = list(full_data_stocks_total_days[full_data_stocks_total_days != 'None'])
        # full_data_stocks_trading_days = np.array([x['symbol'] if x['total_trading_days'] == max(stocks_trading_days) else 'None' for x in stocks_summary])
        # full_data_stocks_trading_days = list(full_data_stocks_trading_days[full_data_stocks_trading_days != 'None'])
        return snp500_stocks
