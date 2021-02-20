from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData

from influxdb import InfluxDBClient
import pandas as pd
import datetime
import logging

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
        print("Finished processing " + self.symbol + ": " + end + " --> " + self.current_date)
        # 9 this is the logical end of your program
        self.just_starting = True
        app.disconnect()

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

start_date = '20210219  00:00:00'
end_date = '20210101  00:00:00'

time_format = "%Y%m%d %H:%M:%S"

stocks_info = pd.read_csv('influxDB/nasdaq_stocks.csv')
for stock_symbol in list(stocks_info['Symbol']):
    my_wrapper = MyWrapper()

    my_wrapper.current_date = start_date
    my_wrapper.sampling_rate = "5"  # seconds
    my_wrapper.symbol = stock_symbol

    while datetime.datetime.strptime(my_wrapper.current_date, time_format) > datetime.datetime.strptime(end_date, time_format):
        try:
            app = EClient(my_wrapper)
            app.connect('127.0.0.1', 7496, clientId=123)
            app.run()
        finally:
            if my_wrapper.the_app_is_down:
                exit()
            else:
                app = EClient(my_wrapper)
                app.connect('127.0.0.1', 7496, clientId=123)
                app.run()
