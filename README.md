# Stock-Market-Research

Great references and summary of articles and code: <br>
https://github.com/sangyx/deep-finance

Implementation of hierarchical attention based mechanism for stocks prediction: <br>
https://github.com/dmis-lab/hats 

In our project we gathered data of 3K companies from the Nasdaq Market. <br>
We implemented the HATS model (by the article above), which uses relational data for stock market prediction.
With the demand above, we used only the S&P500 data (whose relational data is provided by the article researches).
Our mission is to predict, for every compnay, whether it about to increase/decrease or stay neutral.
We predict the trend for all companies in the same time, via the same model!

## Project Workflow
Our work can be devided into 4 sections: Data Collection, Pre Process, Process and Post Process.
* Data Collection: Interactive Brokers API + Python Script --> InfluxDB on Docker container 
  * Couple of months, 5 minutes resolution, 3K companies. parameters: Open, Close, High, Low, Volume.
* Pre Process: Filter, Interpolation, Normalization, Feature engineering 
* Process (Models): HATS implementation (for the mean time)
* Post Process - tensorboard visualization: scalars (loss, top/bottom-k) and graph

## Sample Results
We measure success by 2 main concepts of top/bottom k hit ratio. which means that we take 
the top k companies that we are most confident with their trend (increase:top and decrease:bottom) and ask, what 
is the percentage of companies that actualy changed according our prediction.

Comparison between different sets of the parameters:  <br>
* 'prediction_interval' - the amount of timestamps into the future of trend prediction
* 'look_back' - the amount of timestamps from the past we consider relevant for the prediciton
* 'min_max_norm_back' - the amount of timestamps from the past we use to norm (min-max normalization) the data
![image](https://user-images.githubusercontent.com/55198967/114267689-d8ef2f80-9a05-11eb-917d-821c345269b8.png)

We can see that in some of the cases the hit-ratio of increasing stocks is around 54%.

## Further Work
General work:
* First of all, we have bunch of TODOs in the project :)
* Next, I would like to implement the model using tf v2 instead of v1
* After all the above, I would try and collect more data (2 years instead of 2 months) and analyze the results for windowed periods over the data time zone.

Research work:
* Build and test new relational data by the concepts described in the article and more
  * see: [Organizations Properties](https://www.wikidata.org/wiki/Wikidata:List_of_properties/organization)
* Compare the success of the model with and without the attention mechanism
