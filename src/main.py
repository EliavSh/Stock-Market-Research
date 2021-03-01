from copy import deepcopy

from src import *

# filter stocks by: keep only the stocks with the maximum trading days in their record (our database)
stocks_data = FilterEnum.MaxTradingDays.get().get_filtered_data()

# interpolate data: fill missing times by next values, except the volume - fill with zeros
InterpolationEnum.BasicInterpolation.get().interpolate(stocks_data=stocks_data)

# save the raw stocks data before normalizing for loss calculations
raw_stocks_data = deepcopy(stocks_data)

# normalize data
NormalizerEnum.BasicNormalizer.get().normalize(stocks_data)

# process

print("king")
