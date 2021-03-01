import time
from typing import Dict, List
import pandas as pd
import math

from .abstract_normalizer import AbstractNormalizer
from src.influx_db import influx_utils


class BasicNormalizer(AbstractNormalizer):

    def normalize(self, stocks_list: Dict[str, List[list]]) -> None:
        start_time = time.time()

        time_index = influx_utils.get_field_indices(['time'])[0]
        values_indices = influx_utils.get_field_indices(['close', 'high', 'low', 'open'])
        volume_index = influx_utils.get_field_indices(['volume'])[0]

        for stock in stocks_list.keys():
            # remove the first time point
            stocks_list[stock][time_index] = stocks_list[stock][time_index][1:]

            # normalize the values: [close, high, low, open] by change rate: value -> (value - last_value)/last_value
            # TODO - analyze the influence of the small values we create here, maybe we should do just value/last_value?
            for value in values_indices:
                stocks_list[stock][value] = list(pd.Series(stocks_list[stock][value]).diff().values[1:] / pd.Series(stocks_list[stock][value]).values[:-1])

            # normalize volume by multiplying with 10^-3
            stocks_list[stock][volume_index] = [vol * math.pow(10, -3) for vol in stocks_list[stock][volume_index]][1:]
        print('Normalization took: ' + "{:.2f}".format(time.time() - start_time) + ' seconds.\n')
