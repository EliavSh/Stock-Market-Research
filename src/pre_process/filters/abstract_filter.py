import time
from abc import abstractmethod, ABC
from typing import List, Dict

import numpy as np
from influxdb import InfluxDBClient

from src.influx_db import influx_utils
from src.influx_db.influx_utils import InfluxUtils


class AbstractFilter(ABC):

    def __init__(self):
        self.client = InfluxDBClient()
        self.client.switch_database(self.client.get_list_database()[1]['name'])
        self.influxUtils = InfluxUtils(client=self.client)

    @abstractmethod
    def filter(self) -> List[str]:
        raise NotImplementedError

    def get_filtered_data(self) -> Dict[str, List[List]]:
        """
        This method is the same for all filters, we take the list of stocks and gather their data from our database
        :return: Dict of filtered stocks, such that each value contains the data of the stock by 'InfluxUtils,STOCK_FIELDS'
        """
        start_time = time.time()
        stocks = str(self.filter()).replace('\'', '').replace(' ', '').replace(']', '').replace('[', '')
        query_result = self.client.query(
            'SELECT *::FIELD FROM "stock_market"."autogen".' + stocks +
            ' WHERE time > ' + str(int(self.influxUtils.datetime_to_timestamp(influx_utils.FIRST_DATETIME_OF_DATA)) * 10 ** 9) + ' AND time < ' + str(
                int(self.influxUtils.datetime_to_timestamp(influx_utils.LAST_DATETIME_OF_DATE)) * 10 ** 9))

        # now we convert the structure of query results for convenience
        # we should take into account that huge dict of lists is WAY more expensive than list of tiny dicts.
        # ex: for 600 stocks, "query_results" size is ~4800 bytes while "stocks_data" is ~18500 bytes!
        stocks_data = {}
        for result in query_result.raw['series']:
            field_names = result['columns']
            field_values = result['values']
            ii = np.where(np.array([x in influx_utils.STOCK_FIELDS for x in field_names]))  # all the interesting indices by STOCK_FIELDS
            stocks_data[result['name']] = [[x[i] for x in field_values] for i in list(*ii)]
        print('Filtering took: ' + "{:.2f}".format(time.time() - start_time) + ' seconds.\n')
        return stocks_data
