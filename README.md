# Stock-Market-Research

Great references and summary of articles and code: <br>
https://github.com/sangyx/deep-finance

Implementation of hierarchical attention based mechanism for stocks prediction: <br>
https://github.com/dmis-lab/hats 

In our project we gathered data of 3K companies from the Nasdaq Market. <br>
We implemented the HATS model (by the article above), which uses relational data for stock market prediction.
With the demand above, we used only the S&P500 data (whom relational data is provided by the article researches).
Our mission is to predict for every compnay, whether it about to increase/decrease or stay neutral.

## Project Workflow
Our work can be devided into 4 sections: Data Collection, PreProcess, Process and PostProcess.
* Data Collection: Interactive Brokers API + Python Script --> InfluxDB on Docker container 
  * Couple of months, 5 minutes resolution, 3K companies. parameters: Open, Close, High, Low, Volume.
* PreProcess: Filter, Interpolation, Normalization, Feature engineering 
* Process (Models): HATS implementation
* PostProcess - tensorboard visualization: params and graph

## Sample Results
We measure success by 2 main concepts of top/bottom k hit ratio. which means that we take 
the top k companies that we are most confident with their trend and ask, what 
is the percentage of companies that actualy changed according our prediction?

Comparison between different sets of the parameters:  <br>
* 'prediction_interval' - the amount of timestamps into the future of trend prediction
* 'look_back' - the amount of timestamps from the past we consider relevant for the prediciton
* 'min_max_norm_back' - the amount of timestamps from the past we use to norm (min-max normalization) the data
![image](https://user-images.githubusercontent.com/55198967/114267689-d8ef2f80-9a05-11eb-917d-821c345269b8.png)
