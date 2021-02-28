from pre_process import *

# filter stocks by available filter
max_days_filter = FilterEnum.MaxTradingDays.get()
stocks_data = max_days_filter.get_filtered_data()

# interpolate data by available interpolator
basic_interpolation = InterpolationEnum.BasicInterpolation.get()
interpolated_data = basic_interpolation.interpolate(stocks_data=stocks_data)

print("king")
