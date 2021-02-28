from .maximum_days import MaximumDaysFilter


class MaxTotalDays(MaximumDaysFilter):

    def get_key(self):
        return 'total_days'
