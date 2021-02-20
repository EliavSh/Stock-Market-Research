import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData

from influxdb import InfluxDBClient
import pandas as pd
import datetime
import logging

from InfluxDB.MyThread import MyThread

"""
In this script we get data from some time-point backwards to another
"""
logging.basicConfig(filename="file.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


def write_data_point(symbol, bar):
    json = [
        {
            "measurement": symbol,
            "tags": {},
            "time": (datetime.datetime.strptime(bar.date, "%Y%m%d  %H:%M:%S") - datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S'),
            "fields": bar.__dict__
        }
    ]
    influx_client.write_points(json)


class MyWrapper(EWrapper):

    def __init__(self):
        super().__init__()
        self.symbol = ""
        self.current_date = ""
        self.sampling_rate = ""
        self.just_starting = True
        self.the_app_is_down = False
        self.nextValidOrderId = 0

    def nextValidId(self, orderId: int):
        # 4 first message received is this one
        # print("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        # 5 start requests here
        self.start()

    def historicalData(self, reqId: int, bar: BarData):
        # 7 data is received for every bar
        # print("HistoricalData. ReqId:", reqId, "BarData.", bar)
        if self.just_starting:
            self.current_date = bar.date
            self.just_starting = False
        write_data_point(self.symbol, bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        # 8 data is finished
        # print("Started processing at: " + end)
        # print("Finished processing at: " + self.current_date)
        print("Finished processing " + self.symbol + ": " + self.convert_time(end) + " --> " + self.convert_time(self.current_date))
        # 9 this is the logical end of your program
        self.just_starting = True
        app.disconnect()

    @staticmethod
    def convert_time(t):
        return datetime.datetime.strptime(t, "%Y%m%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")

    def error(self, reqId, errorCode, errorString):
        # these messages can come anytime.
        # print("Error. Id: ", reqId, " Code: ", errorCode, " Msg: ", errorString)
        if "Enable ActiveX and Socket EClients".lower() in errorString.lower():
            self.the_app_is_down = True

    def start(self):
        if self.current_date.__len__() == 0 or self.sampling_rate.__len__() == 0:
            raise Exception("Error!!! You must initiate the attributes of MyWrapper class!")
        # queryTime = (datetime.datetime.today() - datetime.timedelta(days=6)).strftime("%Y%m%d %H:%M:%S")
        queryTime = self.current_date

        contract = Contract()

        contract.symbol = self.symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = "NASDAQ"

        app.reqHistoricalData(8, contract, queryTime, "86400 S", self.sampling_rate + " mins", "TRADES", 1, 1, False, [])


influx_client = InfluxDBClient()
influx_client.switch_database(influx_client.get_list_database()[1]['name'])
processed_stocks = list(map(lambda x: x['name'], influx_client.get_list_measurements()))
list(map(lambda x: processed_stocks.remove(x), ['ACOR', 'ACRS', 'ACRX']))

start_date = '20210219  00:00:00'
end_date = '20210101  00:00:00'

time_format = "%Y%m%d %H:%M:%S"

stocks_info = pd.read_csv('influxDB/nasdaq_stocks.csv')

start_processing_time = time.time()


def main():
    my_thread = MyThread(app)  # initiating 'my_thread' inside the function ensures it is killed after exiting the 'main' function
    my_thread.start()
    # print('Started processing: ' + stock_symbol + ', at: ' + str(time.time() - start_processing_time))
    time.sleep(24)  # sleep for the period of time the collection of data should take - expected 4 minutes per stock, and 10 extractions for the period with set
    app.disconnect()  # this disconnection ensures that the app isn't connected after 'main' and 'my' threads are done


for stock_symbol in list(stocks_info['Symbol']):
    if stock_symbol in processed_stocks:
        # if we already gathered the information about a stock, move on..
        continue

    my_wrapper = MyWrapper()

    my_wrapper.current_date = start_date
    my_wrapper.sampling_rate = "5"  # minutes
    my_wrapper.symbol = stock_symbol

    while datetime.datetime.strptime(my_wrapper.current_date, time_format) > datetime.datetime.strptime(end_date, time_format):
        try:
            # the duplication of the following three lines allows us to extract continuous data on the same stock
            # another effect of this implementation is at least two rounds of data extraction
            # to sum up, the following code works but sometimes will extract extra data - its OK by me :)
            app = EClient(my_wrapper)
            app.connect('127.0.0.1', 7496, clientId=123)
            main()
        finally:
            if my_wrapper.the_app_is_down:
                exit()
            else:
                app = EClient(my_wrapper)
                app.connect('127.0.0.1', 7496, clientId=123)
                main()
