import sys
sys.path.append('src/util')
import requests
import pandas as pd
import numpy as np
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

np.seterr(divide='ignore', invalid='ignore')
load_dotenv(dotenv_path='stock.env')

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

data_location = os.getenv("data")
intraday = os.getenv("data") + os.getenv("intraday")
tz = os.getenv("timezone")
date_format = os.getenv("date_format")
datetime_format = os.getenv("datetime_format")

stocks = ['VN30', 'VN30F1M', 'VN30F2M', "VNINDEX"]
timeframes = ['5', '15', '60', 'D']

msgBottom = 'Bottom'
msgTop = "Top"

# PDI forming a bottom and NDI forming a top
def checkBottom(df, rowIndex):
    row = df.iloc[rowIndex]
    prow = df.iloc[rowIndex + 1]
    maxNDI = round(max(list(df.loc[rowIndex:rowIndex+5].NDI)), 0)
    isNDIOnTop = (row.NDI < maxNDI) and (row.NDI >= 30) and (maxNDI >= round(row.ADX, 0))
    minPDI = min(list(df.loc[rowIndex:rowIndex+5].PDI))
    isPDIOnBottom = (row.PDI > minPDI) and (row.PDI < 25) and (row.PDI > prow.PDI)
    isHistogramIncreased = row.Histogram > prow.Histogram
    # isBelowMA200 = row.Close < row.MA200
    minStoch = round(min(list(df.loc[rowIndex:rowIndex+5]['%D'])), 0)
    isStochOverSold = minStoch <= 25
    return isNDIOnTop and isPDIOnBottom and isHistogramIncreased and isStochOverSold

# PDI forming a bottom and NDI forming a top when above MA200
def checkTop(df, rowIndex):
    row = df.iloc[rowIndex]
    prow = df.iloc[rowIndex + 1]
    maxPDI = round(max(list(df.loc[rowIndex:rowIndex+5].PDI)), 0)
    isNDIOnTop = (row.PDI < maxPDI) and (row.PDI >= 30) and (maxPDI >= round(row.ADX, 0))
    minNDI = min(list(df.loc[rowIndex:rowIndex+5].NDI))
    isNDIOnBottom = (row.NDI > minNDI) and (row.NDI < 25) and (row.NDI > prow.NDI)
    isHistogramDecreased = row.Histogram < prow.Histogram
    maxStoch = round(max(list(df.loc[rowIndex:rowIndex+5]['%D'])), 0)
    isStochOverBought = maxStoch >= 75
    return isNDIOnTop and isNDIOnBottom and isHistogramDecreased and isStochOverBought

# ADX forming a bottom while PDI increasing and NDI decreasing
def checkBottomOnCorrection(df, rowIndex):
    row = df.iloc[rowIndex]
    prow = df.iloc[rowIndex + 1]
    minADX = round(min(list(df.loc[rowIndex:rowIndex+5].ADX)), 0)
    isADXOnBottom = (row.ADX > prow.ADX) and (row.ADX < 25) and (row.ADX > minADX) and (df.iloc[rowIndex + 5].ADX > minADX)
    isPDIIncreased = (row.PDI > prow.PDI) and (row.PDI >= row.NDI)
    isHistogramIncreased = row.Histogram > prow.Histogram
    isMACDNegative = row.MACD_SIGNAL < 0
    isAboveMA200 = row.Close > row.MA200
    minStoch = round(min(list(df.loc[rowIndex:rowIndex+5]['%D'])), 0)
    isStochOverSold = minStoch <= 25
    if isADXOnBottom and isPDIIncreased:
        print(df.iloc[rowIndex].Date, "ADX Bottom and Increasing")
    return isADXOnBottom and isPDIIncreased and isHistogramIncreased and isAboveMA200 and isStochOverSold and isMACDNegative

# ADX forming a bottom while PDI increasing and NDI decreasing
def checkTopOnCorrection(df, rowIndex):
    row = df.iloc[rowIndex]
    prow = df.iloc[rowIndex + 1]
    minADX = round(min(list(df.loc[rowIndex:rowIndex+5].ADX)), 0)
    isADXOnBottom = (row.ADX > prow.ADX) and (row.ADX < 25) and (row.ADX > minADX) and (df.iloc[rowIndex + 5].ADX > minADX)
    isNDIIncreased = (row.NDI > prow.NDI) and (row.NDI >= row.PDI)
    isHistogramDecreased = row.Histogram < prow.Histogram
    isMACDPossitive = row.MACD_SIGNAL > 0
    isBelowMA200 = row.Close < row.MA200
    maxStoch = round(max(list(df.loc[rowIndex:rowIndex+5]['%D'])), 0)
    isStochOverBought = maxStoch <= 75
    if isADXOnBottom and isNDIIncreased:
        print(df.iloc[rowIndex].Date, "ADX Bottom and Decreasing")
    return isADXOnBottom and isNDIIncreased and isHistogramDecreased and isBelowMA200 and isStochOverBought and isMACDPossitive

def filterStocks(stocks, rowIndex):
    topStocks = []
    bottomStocks = []
    bottomCorrectionStocks = []
    topCorrectionStocks = []
    date = ""
    for stock in stocks:
        logger.info("Scanning {}".format(stock))
        df = pd.read_csv("{}{}.csv".format(intraday, stock))
        # subDf = pd.read_csv("{}{}_{}.csv".format(intraday, smallTimeframe, stock))
        date = df.iloc[rowIndex].Date
        getIndicators(df)
        if checkTop(df, rowIndex):
            topStocks.append(stock)
        if checkBottom(df, rowIndex):
            bottomStocks.append(stock)
        if checkTopOnCorrection(df, rowIndex):
            topCorrectionStocks.append(stock)
        if checkBottomOnCorrection(df, rowIndex):
            bottomCorrectionStocks.append(stock)
    return (date, topStocks, bottomStocks, topCorrectionStocks, bottomCorrectionStocks)

def scan(stocks, rowIndex):
    (date, topStocks, bottomStocks, topCorrectionStocks, bottomCorrectionStocks) = filterStocks(stocks, rowIndex)
    print("Scanning on {}".format(date))
    if len(topStocks) > 0:
        print(msgTop)
        print(",".join(topStocks))
    if len(bottomStocks) > 0:
        print(msgBottom)
        print(",".join(bottomStocks))
    if len(topCorrectionStocks) > 0:
        print("Top correction")
        print(",".join(topCorrectionStocks))
    if len(bottomCorrectionStocks) > 0:
        print("Bottom correction")
        print(",".join(bottomCorrectionStocks))


def reportFoundStocks(stocks, rowIndex):
    (date, bottomOnUptrendStocks, bottomStocks, bottomCorrectionStocks, bottomCorrectionStocksV2) = filterStocks(stocks, rowIndex)
    message = "<H2>Scanning on {}</H2>".format(date)
    if len(bottomStocks) > 0:
        message = message + "<h3>{}</h3>".format(msgBottom) + "\n"
        message = message + ",".join(bottomStocks)
    if len(bottomCorrectionStocks) > 0:
        message = message + "<h3>Bottom correction:</h3>" + "\n"
        message = message + ",".join(bottomCorrectionStocks)
    if len(bottomCorrectionStocksV2) > 0:
        message = message + "<h3>Bottom correction V2 (MACD SIGNAL can be above 0):</h3>" + "\n"
        message = message + ",".join(bottomCorrectionStocksV2)
    message = message + "\n\n<b>Please check Stoch divergence, trendlines, MA and other resistances<b>\n"
    message = message + "<b>Exit trade early if you enter for Bottom stocks breaking down MA200<b>"
    sendEmail("Scan Stock Patterns", message, "html")

def checkStock(stock):
    df = pd.read_csv("{}{}.csv".format(intraday, stock))
    # subDf = pd.read_csv("{}{}_{}.csv".format(intraday, smallTimeframe, stock))
    getIndicators(df)
    for rowIndex in reversed(range(len(df) - 200)):
        # if df.iloc[i].Date == "2021-07-15":
            patterns = []
            if checkTop(df, rowIndex):
                patterns.append(msgTop)
            if checkBottom(df, rowIndex):
                patterns.append(msgBottom)
            if checkTopOnCorrection(df, rowIndex):
                patterns.append("Top correction")
            if checkBottomOnCorrection(df, rowIndex):
                patterns.append("Bottom correction")
            if len(patterns) > 0:
                print(df.iloc[rowIndex].Date, ",".join(patterns))

def scanStocks(stocks):
    scan(stocks, 0)

def scanHistoricalStocks(stocks):
    for i in (1, 5):
        scan(stocks, i)

def getStocks():
    all_stocks = []
    for stock in stocks:
        for timeframe in timeframes:
            all_stocks.append("{}_{}".format(timeframe, stock))
    return all_stocks

if __name__ == "__main__":
    all_stocks = getStocks()
    if (len(sys.argv) == 1):    
        scanStocks(all_stocks)
    if (len(sys.argv) == 2):
        if(sys.argv[1] == 'history'):
            scanHistoricalStocks(all_stocks)
        if len(sys.argv[1]) != 'email':
            print("Check stock")
            checkStock(sys.argv[1])
        if (sys.argv[1] == "email"):
            reportFoundStocks(all_stocks, 0)
