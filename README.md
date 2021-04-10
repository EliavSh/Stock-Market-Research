# Stock-Market-Research

Great references and summary of articles and code: <br>
https://github.com/sangyx/deep-finance

Implementation of hierarchical attention based mechanism for stocks prediction: <br>
https://github.com/dmis-lab/hats 

## Project Pipline
1. Data Collection: Interactive Brokers API + Python Script --> InfluxDB on Docker container 
* Couple months of 5 minutes resolution. params: Open|Close|High|Low|Volume.
2. PreProcess: Filter, Interpolation, Normalization, Feature engineering 
3. Process (Models): HATS implementation
4. PostProcess - tensorboard visualization: params and graph

## Sample Results
Comparison between different sets of the parameters:  <br>
* 'prediction_interval' - the amount of timestamps into the future of trend prediction
* 'look_back' - the amount of timestamps from the past we consider relevant for the prediciton
* 'min_max_norm_back' - the amount of timestamps from the past we use to norm (min-max normalization) the data
![image](https://user-images.githubusercontent.com/55198967/114267689-d8ef2f80-9a05-11eb-917d-821c345269b8.png)
