from enum import Enum
from src.pre_process.filters.max_filters import *
from .abstract_filter import AbstractFilter


class FilterEnum(Enum):
    MaxTotalDays = MaxTotalDays
    MaxTradingDays = MaxTradingDays
    # TODO - implement filters by volume, sector, market_cap AND implement mixtures as well

    def get(self) -> AbstractFilter:
        # The object instantiates only when calling it with 'get', instead of within the enum values
        return self.value()
