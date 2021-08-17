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
date = getLastTradingDay()
stocks = ['VN30F2108']

def showBigBoys():
    for stock in stocks:
        df = pd.read_csv("{}{}/{}.csv".format(transaction, stock, date))
        df = df[(df.Side == 'B') | (df.Side == 'S')]
        df300 = df[df.Volume > 300]
        if len(df300) > 0:
            print("BigBoys 300 of {}".format(stock))
            print(df300.tail(20))
        df100 = df[df.Volume > 100]
        if len(df100) > 0:
            print("BigBoys 100 of {}".format(stock))
            print(df100.tail(20))

def showCashflowReport():
    for stock in stocks:
        print("Cashflow report for {}".format(stock))
        df = pd.read_csv("{}{}/{}.csv".format(transaction, stock, date))
        df = df[(df.Side == 'B') | (df.Side == 'S')]
        sideDict  = df.groupby(['Side']).agg('count')['DateTime'].to_dict()
        print(sideDict)
        df = df[df.Volume > 200]
        sideDict  = df.groupby(['Side']).agg('count')['DateTime'].to_dict()
        print("Cashflow Big Boys report for {}".format(stock))
        print(sideDict)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        showCashflowReport()
    elif (sys.argv[1] == 'bigboy'):
        showBigBoys()