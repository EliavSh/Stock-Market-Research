from typing import List
import pandas as pd

from .abstract_filter import AbstractFilter


class RelationFilter(AbstractFilter):

    def filter(self) -> List[str]:
        return pd.read_pickle('./pre_process/data_utils/ordered_ticker.pkl')
