from typing import List

from influxdb import InfluxDBClient as Client
import numpy as np

from InfluxDB.influx_utils import InfluxUtils
from abstract_filter import AbstractFilter


class MaximumDays(AbstractFilter):

    def __init__(self):
        self.client = Client()
        self.client.switch_database(self.client.get_list_database()[1]['name'])
        self.influxUtils = InfluxUtils(client=self.client)

    def filter(self) -> List[str]:
        # get all stocks
        stocks_summary = [self.influxUtils.get_stock_summary(x) for x in list(map(lambda x: x['name'], self.client.get_list_measurements()))]
        stocks_total_days = list(map(lambda x: x['total_days'], stocks_summary))

        # get a list of the stocks with the entire data
        full_data_stocks = np.array([x['symbol'] if x['total_days'] == max(stocks_total_days) else 'None' for x in stocks_summary])
        return list(full_data_stocks[full_data_stocks != 'None'])
