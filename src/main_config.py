class MainConfig:
    def __init__(self):
        self.look_back = 20
        self.features = ['close', 'volume']
        self.label = 'close'
        # TODO - remove one of these...
        self.n_classes = 3
        self.num_classes = 3
        self.n_epochs = 100
        self.prediction_interval = None
        self.top_k_percent = 10  # % of companies we use for calculating the model success
