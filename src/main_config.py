class MainConfig:
    look_back = 10  # TODO - the other config have the same variable too... FIX THAT!!!
    features = ['close', 'volume']
    label = 'close'
    n_classes = 3
    num_classes = 3
    n_epochs = 300
    prediction_intervals = [3, 6, 9, 12]  # list of intervals of length of 5 minutes, ex: 6 means 6*5=30 minutes prediction
