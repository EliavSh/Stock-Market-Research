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

    @abstractmethod
    def build_model(self):
        raise NotImplementedError
