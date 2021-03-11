import numpy as np
import pandas as pd

from src.main_config import MainConfig

# TODO - move it to config!
train_start = 0.
train_end = 0.8
test_start = 0.8
test_end = 1.

prediction_intervals = 6  # predicting the return of the next 5*6=30 minutes


class TimeSeriesSplit:
    """
    In this class we are going to split the data into two sets: train and test.
    Each set consists of batches of samples by some 'look_back' configuration-value.
    Each sample of a set is a tuple of:
    1. input fields
    2. boolean class 'hot' 1D-array (length is number_of_classes)
    3. output field
    """

    def __init__(self, stocks_data):
        self.stocks_data = stocks_data
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end

        self.label = MainConfig.label
        self.features = MainConfig.features
        self.look_back = MainConfig.look_back

        self.n_classes = MainConfig.n_classes
        self.thresholds = []

    def train_test_split(self):
        self.validate_data()

        # rearrange the array to dimension: (time_stamps, companies, features)
        data = np.moveaxis(np.array(list(self.stocks_data.values())), -1, 0)
        data = data[:, :, 1:].astype(float)  # we don't need the time column any more

        self.calc_thresholds(data)

        # refactor the data to dimension: (time_stamps, companies, look_back, features)
        look_backed_data = []
        # TODO - use the mean data until - 1 - num_intervals
        for t in range(self.look_back, len(data[self.look_back:] - 1)):  # -1 for getting the target value: the next value of every sample
            # append (x,y) tuples where x is the look_backed data and y is the target_value of the next time-stamp (t+1)
            x = np.moveaxis(data[t - self.look_back:t, :, :], 0, 1)
            # TODO - add a configuration of the time range we want to predict - without nothing changed its at 5min frequency
            numeric_y = data[t + 1, :, self.features.index(self.label)]
            look_backed_data.append((x, self.numeric_to_label(numeric_y), numeric_y))

        # slice the looked_back_data to train and test
        length = len(look_backed_data)
        train_set = look_backed_data[int(train_start * length):int(train_end * length)]
        test_set = look_backed_data[int(test_start * length):int(test_end * length)]

        self.train_test_summary('Train', train_set)
        self.train_test_summary('Test', test_set)

        return train_set, test_set

    def numeric_to_label(self, numeric_y):
        labeled_y = []
        for y_val in numeric_y:
            label = np.zeros(self.n_classes)
            label[sum(y_val > self.thresholds)] = 1  # set 1 for the index (class) between thresholds
            labeled_y.append(label)
        return labeled_y

    def calc_thresholds(self, data):
        train_data = data[int(train_start * len(data)):int(train_end * len(data))]
        label_series = pd.Series(np.array([x[:, self.features.index(self.label)] for x in train_data]).flatten())
        self.thresholds = label_series.quantile(np.linspace(0, 1, self.n_classes + 1)[1:-1]).values

    @staticmethod
    def train_test_summary(name, data):
        temp_list = []
        for i in range(len(data)):
            temp_list.append([np.where(x == 1.)[0][0] for x in data[i][1]])
        values, counts = np.unique(np.array(temp_list).flatten(), return_counts=True)
        print('\n' + name + ' classes:\nValues: ' + str(values) + '\nCounts: ' + str(counts))

    def validate_data(self):
        if not (0 <= train_start < train_end <= test_start < test_end <= 1):
            print('Something wrong with testing/training start/end values!')
            exit()

        if self.look_back > len(self.stocks_data):
            print("Couldn't split the data, look back is too big!")
            exit()

        if self.n_classes < 2:
            print('number of classes must > 1')
            exit()
