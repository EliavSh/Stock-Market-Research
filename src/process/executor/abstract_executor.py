from abc import abstractmethod, ABC
from typing import List
import numpy as np


class AbstractExecutor(ABC):
    """
    The Class is responsible of the phases: training and testing.
    We execute the epochs of each phase for n_epochs.
    """

    def __init__(self, config):
        self.n_epochs = config.n_epochs

        self.log_dir = "tensorboard/" + self.conf_to_string(config)

    @staticmethod
    def conf_to_string(c):
        return "prediction_interval_%s__look_back_%s__min_max_back_%s" % (c.prediction_intervals, c.look_back, c.min_max_norm_intervals)

    def start(self, train_set, test_set):
        """
        Starting the entire train and test phases, while aggregating losses
        """
        all_train_losses, all_test_losses = [], []
        for cur_epoch in range(self.n_epochs):
            # execute train and test (test is without learning)
            train_losses = self.epoch(cur_epoch, train_set, "train")
            test_losses = self.epoch(cur_epoch, test_set, "test")

            # record losses and prepare for next epoch
            all_train_losses.append(train_losses)
            all_test_losses.append(test_losses)

        print('king')

    def epoch(self, cur_epoch, data_set, phase):
        """
        Abstract epoch flow, passing through the entire data (no batching)
        """
        losses = []
        for (timestamp, timestamp_data) in enumerate(zip(data_set)):
            x, y, rt = timestamp_data[0]
            my_loss, metrics = self.step(x, y, rt, cur_epoch, timestamp, len(data_set), phase)
            losses.append(my_loss)
        return losses

    @abstractmethod
    def step(self, x: np.array, y: List, rt: np.array, cur_epoch: int, timestamp: int, len_data: int, phase: str):
        raise NotImplementedError
