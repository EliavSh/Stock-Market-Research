from .maximum_days import MaximumDaysFilter


class MaxTradingDays(MaximumDaysFilter):

    def get_key(self):
        return 'total_trading_days'
