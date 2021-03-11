import tensorflow as tf
from copy import deepcopy
from src import *

# filter stocks by: keep only the stocks with the maximum trading days in their record (our database)
stocks_data = FilterEnum.IntersectionFilter.get(FilterEnum.SNP500Filter.get(),
                                                FilterEnum.MaxTradingDays.get(),
                                                FilterEnum.RelationFilter.get()).get_filtered_data()

# interpolate data: fill missing times by next values, except the volume - fill with zeros
InterpolationEnum.BasicInterpolation.get().interpolate(stocks_data=stocks_data)

# save the raw stocks data before normalizing for loss calculations
raw_stocks_data = deepcopy(stocks_data)

# normalize data
NormalizerEnum.BasicNormalizer.get().normalize(stocks_data)

# split data to train and test
train_set, test_set = TimeSeriesSplit(stocks_data).train_test_split()

# process
sess = tf.Session()

LOGDIR = "tensorboard_temp/temp"
writer = tf.compat.v1.summary.FileWriter(LOGDIR)

model = BasicExecutor(sess, writer, ModelEnum.HATS, train_set, list(stocks_data.keys()))
# writer.add_graph(sess.graph)

model.train()  # TODO - fix the error here

print("king")
