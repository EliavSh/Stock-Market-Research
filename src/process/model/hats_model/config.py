class Config:
    features = ['close', 'volume']
    label = ['close']
    num_classes = 3
    look_back = 10  # TODO - the other config has the same value in another variable.. FIX THAT!!!
    neighbors_sample = 20
    lr = 0.001
    node_feat_size = 128
    rel_attention = True
    n_epochs = 300
    dropout = 0.3
