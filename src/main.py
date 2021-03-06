import tensorflow as tf
from src import *
from multiprocessing import Process


def conf_to_string(c: MainConfig):
    return "prediction_interval_%s__look_back_%s__min_max_back_%s" % (c.prediction_intervals, c.look_back, c.min_max_norm_intervals)


def main(conf):
    # filter stocks by: keep only the stocks with the maximum trading days in their record (our database)
    stocks_data = FilterEnum.IntersectionFilter.get(conf, FilterEnum.SNP500Filter.get(conf),
                                                    FilterEnum.MaxTradingDays.get(conf),
                                                    FilterEnum.RelationFilter.get(conf)).get_filtered_data()

    # interpolate data: fill missing times by next values, except the volume - fill with zeros
    InterpolationEnum.BasicInterpolation.get().interpolate(stocks_data=stocks_data)

    # normalize data
    NormalizerEnum.BasicNormalizer.get(conf).normalize(stocks_data)

    # TODO - add indicators (as features) of pre/after/start/end of the market

    # split data to train and test
    train_set, test_set = TimeSeriesSplit(stocks_data, conf).train_test_split()

    # process
    sess = tf.Session()

    log_dir = "tensorboard/" + conf_to_string(conf)
    writer = tf.compat.v1.summary.FileWriter(log_dir)

    my_executor = BasicExecutor(sess, writer, ModelEnum.HATS, list(stocks_data.keys()), conf)
    writer.add_graph(sess.graph)

    my_executor.start(train_set, test_set)

    print("king")


if __name__ == '__main__':
    temp = True
    if temp:
        config = MainConfig()
        config.prediction_intervals = 24
        main(config)
    else:
        # list of intervals of length of 5 minutes, ex: 6 means 6*5=30 minutes prediction
        prediction_intervals = [3, 6, 9, 12]
        jobs = []
        for prediction_interval in prediction_intervals:
            config = MainConfig()
            config.prediction_intervals = prediction_interval
            p = Process(target=main, args=(config,))
            jobs.append(p)
            p.start()
        for j in jobs:
            j.join()
