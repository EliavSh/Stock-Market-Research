import numpy as np
import tensorflow as tf

from .evaluator import Evaluator
from .abstract_executor import AbstractExecutor
from ..model_enum import ModelEnum


class BasicExecutor(AbstractExecutor):
    """
    This class execute all precesses regards the model: train and test
    """

    def __init__(self, sess, writer, model: ModelEnum, symbols, config):
        self.sess = sess
        self.writer = writer

        self.model = model.get(sess, writer, symbols, config)
        self.evaluator = Evaluator(self.sess, config.num_classes, self.model, config.top_k_percent)

        self.n_epochs = config.n_epochs

        self.summary = tf.Summary()
        self.scalars = []

    def epoch(self, cur_epoch, data_set, phase):
        losses = []
        for (j, timestamp_data) in enumerate(zip(data_set)):
            x, y, rt = timestamp_data[0]
            my_loss, metrics = self.step(x, y, rt, cur_epoch, j, len(data_set), phase)
            losses.append(my_loss)
        return losses

    def add_scalar_to_summary(self, name, value):
        self.scalars.append(tf.summary.scalar(name, value))

    def step(self, x, y, rt, cur_epoch, j, data_length, phase):
        # batch is whole dataset of a single company
        feed_dict = {self.model.x: x, self.model.y: y, self.evaluator.rates: rt}

        # in case of train, we calculating model.optimize and updating network weights by that
        if phase == 'train':
            _, loss, pred, prob, summaries = self.sess.run(
                [self.model.optimize, self.model.cross_entropy, self.model.prediction, self.model.prob, self.evaluator.train_summaries], feed_dict=feed_dict)
        else:
            # otherwise, while testing, only calculate scores and record for summary
            loss, pred, prob, summaries = self.sess.run(
                [self.model.cross_entropy, self.model.prediction, self.model.prob, self.evaluator.test_summaries], feed_dict=feed_dict)

        for s in summaries:
            self.writer.add_summary(s, cur_epoch * data_length + j)

        # for later use
        label = np.argmax(y, 1)
        metrics = self.evaluator.metric(label, pred, prob, rt)

        return loss, metrics

    def start(self, train_set, test_set):
        all_train_losses, all_test_losses = [], []
        for cur_epoch in range(self.model.cur_epoch_tensor.eval(self.sess), self.n_epochs + 1, 1):
            # execute train and test (test is without learning)
            train_losses = self.epoch(cur_epoch, train_set, "train")
            test_losses = self.epoch(cur_epoch, test_set, "test")

            # record losses and prepare for next epoch
            all_train_losses.append(train_losses)
            all_test_losses.append(test_losses)
            self.sess.run(self.model.increment_cur_epoch_tensor)

        print('king')
