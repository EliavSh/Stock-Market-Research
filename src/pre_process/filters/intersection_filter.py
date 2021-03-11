from typing import List

from .abstract_filter import AbstractFilter


class IntersectionFilter(AbstractFilter):

    def __init__(self, *args):
        super().__init__()
        self.filters_list = [*args]

    def filter(self) -> List[str]:
        # list of filtered lists
        filtered_lists = [x.filter() for x in self.filters_list]
        # union of all filtered lists
        symbols = set().union(*filtered_lists)
        # get the intersection of all lists
        for lst in filtered_lists:
            symbols = set(symbols).intersection(lst)
        return list(symbols)
