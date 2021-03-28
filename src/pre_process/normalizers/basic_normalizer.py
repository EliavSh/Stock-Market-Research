import time
from typing import Dict, List
import pandas as pd
import numpy as np

from .abstract_normalizer import AbstractNormalizer
from src.influx_db import influx_utils


class BasicNormalizer(AbstractNormalizer):

    def __init__(self, config):
        self.prediction_intervals = config.prediction_intervals
        self.min_max_norm_intervals = config.min_max_norm_intervals

    def normalize(self, stocks_list: Dict[str, List[list]]) -> None:
        """
        Here we normalize all the fields that are later fed into the model
        Stock-Close-Field - we use the parameter with a rolling diff (period of 1).
        All-fields - reduce range to (0,1) by look-back
        """
        start_time = time.time()

        # TODO - sync with the values here, influx utils and config files!!
        time_index = influx_utils.get_field_indices(['time'])[0]
        values_indices = influx_utils.get_field_indices(['close'])
        volume_index = influx_utils.get_field_indices(['volume'])[0]

        for stock in stocks_list.keys():
            # remove the first time point
            stocks_list[stock][time_index] = stocks_list[stock][time_index][self.prediction_intervals:]

            # normalize the values: [close, high, low, open] by change rate: value -> (value - last_value)/last_value
            for value in values_indices:
                stocks_list[stock][value] = self.rescale(
                    pd.Series(stocks_list[stock][value]).diff(self.prediction_intervals).values[self.prediction_intervals:] / pd.Series(
                        stocks_list[stock][value]).values[:-self.prediction_intervals])

            stocks_list[stock][volume_index] = self.rescale(stocks_list[stock][volume_index][self.prediction_intervals:])
        print('Normalization took: ' + "{:.2f}".format(time.time() - start_time) + ' seconds.\n')

    def rescale(self, array: list or np.array) -> list:
        """
        Rescaling array to range of (0,1)
        Returning array of the same size!
        """
        new_array = np.zeros((len(array),))
        for i in range(len(array)):
            start_scaling_index = 0 if i <= self.min_max_norm_intervals else i - self.min_max_norm_intervals
            if i <= start_scaling_index + 1:
                # mean and diff is meaningful from length of 2 and above
                min_max_range = array[i] or 1
                min_value = 0
            else:
                min_max_range = np.max(array[start_scaling_index:(i + 1)]) - np.min(array[start_scaling_index:(i + 1)]) or np.max(
                    array[start_scaling_index:(i + 1)])
                min_value = np.min(array[start_scaling_index:(i + 1)])
            new_array[i] = (array[i] - min_value) / min_max_range
            assert 1 >= new_array[i] >= 0
        return list(array)
