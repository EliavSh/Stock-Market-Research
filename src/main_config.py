class MainConfig:
    def __init__(self):
        self.look_back = 10
        self.features = ['close', 'volume']
        self.label = 'close'
        self.n_classes = 3
        self.num_classes = 3
        self.n_epochs = 300
        self.prediction_interval = None
