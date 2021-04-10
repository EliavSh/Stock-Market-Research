class MainConfig:
    def __init__(self):
        # rescaling all feature values to range of: (0,1)
        ## notice that this value should be greater than 1 - to avoid rescaling all values to 1
        self.min_max_norm_intervals = 100
        ## notice that this values should be greater than or equals to min_max_norm_intervals - to avoid dealing with inputs that doesn't normalized as the rest
        self.look_back = 48
        self.features = ['close', 'volume']
        self.label = 'close'
        self.num_classes = 3
        self.n_epochs = 100
        self.prediction_intervals = None
        self.top_k_percent = 10  # % of companies we use for calculating the models success
