import sys
sys.path.append('src/util')
import requests
import pandas as pd
import os
from pytz import timezone
from datetime import datetime, date, timedelta
from dateutil.relativedelta import *
from dotenv import load_dotenv
import logging
import logging.config
import math
from utils import *
import json
import schedule
import time

load_dotenv(dotenv_path='future.env')

data_location = os.getenv("data")
intraday = data_location + os.getenv('intraday')
transaction = data_location + os.getenv('transaction')
tz = os.getenv("timezone")
date_format = os.getenv("date_format")
datetime_format = os.getenv("datetime_format")

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

def updateStockTransaction(stock):
    logger.info("Updating transaction {}".format(stock))
    URL = "https://plus24.mbs.com.vn/HO.ashx?DetailFile={}".format(os.getenv(stock))
    rsGetRquest= requests.get(URL)
    tradingData = json.loads(rsGetRquest.text[10:-2])
    if len(tradingData) == 0:
        return
    df = pd.DataFrame(tradingData)
    df.columns = ['DateTime', 'Open', 'Price', 'Volume', 'Time', 'Side', 'D1', 'Total', 'D2', 'D3', 'D4']
    df.DateTime = df.DateTime / 1000
    # df.DateTime = df.apply(lambda x: str(getDatetime(x.DateTime))[0:10], axis=1)
    df.DateTime = df.apply(lambda x: getTransactionDatetime(x.DateTime), axis=1)
    df = df[['DateTime', 'Price', 'Volume', 'Side']]
    date = getLastTradingDay()
    logger.info("Updated {} for {}".format(len(df), stock))
    try:
        oldDf = pd.read_csv("{}{}/{}.csv".format(transaction, stock, date))
    except:
        oldDf = []
    if len(oldDf) > 0:
        # Remove duplicates
        df = pd.concat([df,oldDf]).drop_duplicates().reset_index(drop=True)
    df.to_csv("{}{}/{}.csv".format(transaction, stock, date), index=None)

def updateTransactions():
    stocks = ['VN30F1M', 'VN30F2M']
    for stock in stocks:
        updateStockTransaction(stock)

def updateRealtimeTransactions():
    if isWeekday():
        currentTime = getCurrentTime()
        if ((currentTime >= '09:00') and (currentTime <= '11:30')) or ((currentTime >= '13:00') and (currentTime <= '14:50')):
            updateTransactions()

if __name__ == "__main__":
    if sys.argv[1] == 'history':
        updateTransactions()
    if sys.argv[1] == 'realtime':
        schedule.every(15).seconds.do(updateRealtimeTransactions)
        while True:
            schedule.run_pending()
            time.sleep(1)
