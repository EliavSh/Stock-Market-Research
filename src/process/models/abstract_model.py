from abc import ABC, abstractmethod
import tensorflow as tf


class AbstractModel(ABC):

    def __init__(self):
        self.prediction = None
        self.prob = None
        self.cross_entropy = None
        self.optimize = None
        self.x = None
        self.y = None

        # init the global step
        self.init_global_step()
        # init the epoch counter
        self.init_cur_epoch()

    @abstractmethod
    def build_model(self):
        raise NotImplementedError

    # just initialize a tensorflow variable to use it as global step counter
    def init_global_step(self):
        # DON'T forget to add the global step tensor to the tensorflow trainer
        with tf.variable_scope('global_step'):
            self.global_step_tensor = tf.Variable(0, trainable=False, name='global_step')

    # just initialize a tensorflow variable to use it as epoch counter
    def init_cur_epoch(self):
        with tf.variable_scope('cur_epoch'):
            self.cur_epoch_tensor = tf.Variable(0, trainable=False, name='cur_epoch')
            self.increment_cur_epoch_tensor = tf.assign(self.cur_epoch_tensor, self.cur_epoch_tensor + 1)
