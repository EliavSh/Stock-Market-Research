import datetime
from typing import *


class Utils:
    def __init__(self):
        self.ib_format = "%Y-%m-%dT%H:%M:%SZ"
        self.stock_fields = ['time', 'close', 'high', 'low', 'open', 'volume']

    def generate_datetime_points(self, size: int) -> List[str]:
        datetime_list = []
        for i in range(size):
            datetime_list.append(datetime.datetime.fromtimestamp(1000 * i).strftime(self.ib_format))

        return datetime_list

    def generate_stock_data(self, size: int) -> List[Union[List[str], List[int], List[float]]]:
        """
        Creating stocks_data from 'size' of datetime points and 'range(size)' values for close, high, low, open and volume
        """
        # staring from 1 because stocks values are never exactly zero
        return [self.generate_datetime_points(size), *[list(range(1, size + 1)) for _ in range(len(self.stock_fields) - 1)]]
