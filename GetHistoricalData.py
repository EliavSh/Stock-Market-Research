from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData

import datetime


class MyWrapper(EWrapper):

    def nextValidId(self, orderId: int):
        # 4 first message received is this one
        print("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        # 5 start requests here
        self.start()

    def historicalData(self, reqId: int, bar: BarData):
        # 7 data is received for every bar
        print("HistoricalData. ReqId:", reqId, "BarData.", bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        # 8 data is finished
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        # 9 this is the logical end of your program
        app.disconnect()
        print("finished")

    def error(self, reqId, errorCode, errorString):
        # these messages can come anytime.
        print("Error. Id: ", reqId, " Code: ", errorCode, " Msg: ", errorString)

    def start(self):
        queryTime = (datetime.datetime.today() - datetime.timedelta(days=5)).strftime("%Y%m%d %H:%M:%S")

        contract = Contract()

        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.primaryExchange = "NASDAQ"

        # 6 request data, using fx since I don't have Japanese data
        app.reqHistoricalData(8, contract, queryTime, "150 S", "30 secs", "MIDPOINT", 1, 1, False, [])


app = EClient(MyWrapper())  # 1 create wrapper subclass and pass it to EClient
app.connect("127.0.0.1", 7497, clientId=123)  # 2 connect to TWS/IBG
app.run()  # 3 start message thread
