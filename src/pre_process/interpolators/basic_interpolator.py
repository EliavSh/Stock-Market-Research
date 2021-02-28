from typing import Dict, List
import datetime
import numpy as np
import pandas as pd
from .abstract_interpolator import AbstractInterpolate
from src.influx_db import influx_utils
import time


class BasicInterpolation(AbstractInterpolate):

    def interpolate(self, stocks_data: Dict[str, List[List]]) -> None:
        """
        Fill the missing values of : Close, High, Low, Open with their following/last entry
        Fill the missing volume with zeros
        """
        start_time = time.time()

        time_index = influx_utils.get_field_indices(['time'])[0]
        values_indices = influx_utils.get_field_indices(['close', 'high', 'low', 'open'])
        volume_index = influx_utils.get_field_indices(['volume'])[0]

        # add description of our stocks by the number of timestamps
        time_length_series = pd.Series([len(stocks_data[x][time_index]) for x in stocks_data.keys()])
        print('Description of number of timestamps for our stocks:\n' + str(time_length_series.describe()) + '\n')

        # get the full set of timestamps
        s = set()
        for x in stocks_data.keys():
            for y in stocks_data[x][time_index]:
                s.add(y)

        # sort the timestamps
        lst = list(s)
        lst.sort(key=lambda date: datetime.datetime.strptime(date, influx_utils.IB_DATE_FORMAT))

        # interpolate
        for x in stocks_data.keys():
            # find missing timestamps
            missing_indices = np.array([-1 if timestamp in stocks_data[x][time_index] else i for i, timestamp in enumerate(lst)])

            # add missing values
            for i in missing_indices[missing_indices >= 0]:
                # fix time
                stocks_data[x][time_index].insert(i, lst[i])
                # fix values: c,h,l,o
                for value_index in values_indices:
                    if i < len(stocks_data[x][value_index]):
                        # in case the first/middle values are missing, interpolate with next value
                        stocks_data[x][value_index].insert(i, stocks_data[x][value_index][i])
                    else:
                        # in case the last values are missing, interpolate with previous value
                        stocks_data[x][value_index].insert(i, stocks_data[x][value_index][i - 1])
                # fix volume
                stocks_data[x][volume_index].insert(i, 0)
        print('Interpolating took: ' + "{:.2f}".format(time.time() - start_time) + ' seconds.\n')
