from enum import Enum, unique

from src.pre_process.filters.max_filters import *
from src.pre_process.filters.snp500_filter import SNP500Filter
from src.pre_process.filters.relation_filter import RelationFilter
from src.pre_process.filters.intersection_filter import IntersectionFilter
from .abstract_filter import AbstractFilter


@unique
class FilterEnum(Enum):
    MaxTotalDays = MaxTotalDays
    MaxTradingDays = MaxTradingDays
    SNP500Filter = SNP500Filter
    RelationFilter = RelationFilter
    IntersectionFilter = IntersectionFilter

    # TODO - implement:
    #  *1. relation_data filter (based on the company relations matrix - pickle file)
    #  2. implement filters by volume, sector, market_cap AND implement mixtures as well (no rush)

    def get(self, conf, *args) -> AbstractFilter:
        # The object instantiates only after calling it with 'get'
        return self.value(conf, *args)
