import numpy as np
import tensorflow as tf

from .evaluator_tensor_flow_v1 import EvaluatorTensorFlowV1
from src.process.executor.abstract_executor import AbstractExecutor
from src.process.models.model_enum import ModelEnum


class ExecutorTensorFlowV1(AbstractExecutor):
    """
    This class execute all precesses regards the models: train and test
    Note: should use this class to execute models implemented with tensor-flow v1 only!
    """

    def __init__(self, model: ModelEnum, symbols, config):
        super().__init__(config)
        self.sess = tf.Session()

        self.writer = tf.compat.v1.summary.FileWriter(self.log_dir)
        self.writer.add_graph(self.sess.graph)

        self.model = model.get(self.sess, symbols, config)
        self.evaluator = EvaluatorTensorFlowV1(self.sess, config.num_classes, self.model, config.top_k_percent)

        self.summary = tf.Summary()
        self.scalars = []

    def step(self, x, y, rt, cur_epoch, j, data_length, phase):
        # batch is whole dataset of a single company
        feed_dict = {self.model.x: x, self.model.y: y, self.evaluator.rates: rt}

        # in case of train, we calculating models.optimize and updating network weights by that
        if phase == 'train':
            _, loss, pred, prob, summaries = self.sess.run(
                [self.model.optimize, self.model.cross_entropy, self.model.prediction, self.model.prob, self.evaluator.train_summaries], feed_dict=feed_dict)
        else:
            # otherwise, while testing, only calculate scores and record for summary
            loss, pred, prob, summaries = self.sess.run(
                [self.model.cross_entropy, self.model.prediction, self.model.prob, self.evaluator.test_summaries], feed_dict=feed_dict)

        for s in summaries:
            self.writer.add_summary(s, cur_epoch * data_length + j)

        # TODO - for later use?
        label = np.argmax(y, 1)
        metrics = self.evaluator.metric(label, pred, prob, rt)

        return loss, metrics
