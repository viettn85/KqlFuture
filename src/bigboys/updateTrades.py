import os
import sys
from datetime import datetime
import requests
import pandas as pd

from dotenv import load_dotenv
load_dotenv(dotenv_path='future.env')

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

from contractUtils import getMillisec

def clean(data):
    transactionArr = data[data.find("[") + 1: data.rfind("]")].strip()
    if len(transactionArr) < 2:
        print("There is no transaction")
        return []
    else:
        transactionArr = transactionArr.split(",\n")
        transactionList = []
        for transaction in transactionArr:
            transaction = transaction.replace("\n","").replace("\"","")
            transaction = transaction[1:-1]
            details = transaction.split(",")
            transactionList.append([datetime.fromtimestamp(((int)(details[0]))/1000.0).strftime("%Y-%m-%d"), details[1], details[3], details[4], details[5]])
        df = pd.DataFrame(transactionList)
        return df

def save(df, stock, date):
    logger.info("Saving transactions of {} on {}".format(stock, date))
    df.columns = ['Date', "Price", "Volume", "Time", "Type"]
    df = df[['Date', "Time", "Price", "Volume", "Type"]]
    df = df.astype({'Price': 'float64','Volume': 'int64'})
    # df = df[df.Date == date]
    df = df.sort_values(by=["Date", "Time"], ascending=False)
    df.to_csv(os.getenv('contract_data') + date + "-" + stock + ".csv", index=False)

def getTransactionsByStock(stock, date, time=""):
    logger.info("Getting transactions of {} on {} {}".format(stock, date, time))
    millisec = getMillisec(date, time)
    PARAMS = {
                'DetailFile': stock,
                'lastTime': millisec,
                'callback': os.getenv('contractCallback'),
                '_': "1602053384943"
            }
    # URL = "https://plus24.mbs.com.vn/HO.ashx"
    data = requests.get(url=os.getenv('contractUrl'), params=PARAMS).text
    df = clean(data)
    if len(df) > 0:
        save(df, stock, date)
    else:
        print("No trading of {} on {}".format(stock, date))

def getHistoryTransactionsByStock(stock, fromDate, toDate):
    dates = pd.date_range(fromDate, toDate).tolist()
    for date in dates:
        getTransactions(stock, date.strftime("%Y-%m-%d"))

def getTransactions(stocks, date, time=""):
    stockList = []
    if stocks == "all":
        stockList = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(os.getenv("data_high_vol"))))
        stockList = list(map(lambda stock: stock[0:3], stockList))
    else:
        stockList = stocks.split(",")
    print(len(stockList))
    for stock in stockList:
        # print(stock)
        getTransactionsByStock(stock, date, time)

def getHistoryTransactions(stocks, fromDate, toDate):
    stockList = []
    if stocks == "all":
        stockList = list(filter(lambda x: os.path.splitext(x)
                           [1], os.listdir(os.getenv("data_high_vol"))))
        stockList = map(lambda stock: stock[0:3], stockList)
    else:
        stockList = stocks.split(",")
    for stock in stockList:
        getHistoryTransactionsByStock(stock, fromDate, toDate)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        getTransactions(os.getenv('contractStock'), sys.argv[1])
    if len(sys.argv) == 3:
        getTransactions(os.getenv('contractStock'), sys.argv[1], sys.argv[2])

