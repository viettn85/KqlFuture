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

def updatePriceAndVolume(resolution):
    fromDate = getFromDate(resolution)
    toDate = (datetime.now(timezone(tz)) + relativedelta(days=1)).strftime(date_format)
    startTime = getEpoch(fromDate )
    endTime = getEpoch(toDate)
    stocks = ['VN30F1M', 'VN30F2M', 'VN30', 'VNINDEX']
    for stock in stocks: 
        logger.info('Intraday {} for {}'.format(resolution, stock))
        URL = "https://chartdata1.mbs.com.vn/pbRltCharts/chart/history?symbol={}&resolution={}&from={}&to={}".format(stock, resolution, startTime, endTime)
        response = requests.get(URL)
        # print(response.json())
        newDf = pd.DataFrame(response.json())
        newDf['t']=newDf.apply(lambda x: getIntradayDatetime(x.t) ,axis=1)
        newDf['Change'] = 0
        newDf.rename(columns={"t": "Date", "c": "Close", "o": "Open", "h": "High", "l": "Low", "Change": "Change", "v": "Volume"}, inplace=True)
        newDf = newDf[['Date', 'Close', 'Open', 'High', 'Low', 'Change', 'Volume']]
        newDf.Volume = newDf.Volume * 10
        newDf.Volume = newDf.Volume.astype(int)
        newDf.sort_values(by="Date", ascending=False, inplace=True)
        newDf['Close_Shift'] = newDf.Close.shift(-1)
        newDf.Change = newDf.apply(lambda x: round((x.Close - x.Close_Shift)/x.Close_Shift * 100, 2) ,axis=1)
        newDf.drop('Close_Shift', axis=1, inplace=True)
        newDf[['Close', 'Open', 'High', 'Low']] = round(newDf[['Close', 'Open', 'High', 'Low']], 2)
        newDf.to_csv("{}{}_{}.csv".format(intraday, resolution, stock), index=None)

def append(stock):
    df5 = pd.read_csv("{}{}_{}.csv".format(intraday, '5', 'stock'), index=None).loc[0]
    lastUpdated = df5.iloc[0].Date # 2021-08-13T14:45:00Z
    currentDate = lastUpdated[0:11] + "00:00:00Z"
    currentHour = lastUpdated[0:13] + "00:00Z"
    df = pd.DataFrame.from_dict(
        {
            'Date': [currentDate], 
            'Close': [df5.iloc[0].Date]
        })
    # df15 = pd.read_csv("{}{}_{}.csv".format(intraday, '15', 'stock'), index=None)
    df60 = pd.read_csv("{}{}_{}.csv".format(intraday, '60', 'stock'), index=None)
    df60 = df60[df60.Date != currentHour]
    dfD = pd.read_csv("{}{}_{}.csv".format(intraday, 'D', 'stock'), index=None)
    dfD = df60[dfD.Date != currentDate]


def crawlRecentIntraday():
    logger.info("Get recent intraday data")
    updatePriceAndVolume('D')
    updatePriceAndVolume('60')
    updatePriceAndVolume('15')
    updatePriceAndVolume('5')

if __name__ == "__main__":
    crawlRecentIntraday()
