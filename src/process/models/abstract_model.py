from abc import ABC, abstractmethod


class AbstractModel(ABC):

    def __init__(self, config):
        # load from main_config
        self.n_epochs = config.n_epochs
        self.features = config.features
        self.input_dim = len(config.features)
        self.look_back = config.look_back
        self.n_labels = config.num_classes

        self.prediction = None
        self.prob = None
        self.cross_entropy = None
        self.optimize = None
        self.x = None
        self.y = None

    @abstractmethod
    def build_model(self):
        raise NotImplementedError
