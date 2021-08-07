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
np.seterr(divide='ignore', invalid='ignore')
load_dotenv(dotenv_path='future.env')

logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

data_location = os.getenv("data")
intraday = data_location + os.getenv('intraday')
transaction = data_location + os.getenv('transaction')
tz = os.getenv("timezone")
date_format = os.getenv("date_format")
datetime_format = os.getenv("datetime_format")

def isCrossMA(row, position):
    minMA = min(row.MA200, row.MA50, row.MA20)
    maxMA = max(row.MA200, row.MA50, row.MA20)
    if abs(minMA - maxMA) <= int(os.getenv("ma_distance")):
        if (not position['CrossMA']):
            # print("row.Date", row.Date)
            position['CrossMA'] = True
            return True
    else:
        position['CrossMA'] = False
    return False

def isSoftzone(row, position):
    if (position['CrossMA'] or isCrossMA(row, position)) and (abs(row.Histogram) < int(os.getenv("histogram"))) \
        and (abs(row.MACD) < int(os.getenv("macd"))) and (abs(row.MACD_SIGNAL) < int(os.getenv("macd_signal"))):
        if (not position['SoftZone']):
            position['SoftZone'] = True
            return True
    else:
        position['SoftZone'] = False
    return False

def isUptrend(df, i):
    row = df.loc[i]
    if (row.MA20 > row.MA50) and (row.MA50 > row.MA200):
        return True
    return False

def isDowntrend(df, i):
    row = df.loc[i]
    if (row.MA20 < row.MA50) and (row.MA50 < row.MA200):
        return True
    return False

def isUptrendCorrection(df, i, position):
    try:
        row = df.loc[i]
        prow = df.loc[i+1]
        srow = df.loc[i+10]
        
        if (row.Close < row.MA20) or (row.MA20 < row.MA50) or (row.MA50 < row.MA200) or (row.RSI < 48):
            # position['UptrendCorrection'] = False
            return False
        minMACD = min(list(df.loc[0:10].MACD))
        minStoch = min(list(df.loc[0:10]['%K']))
        if row.Date == '2021-06-15T13:00:00Z':
            print((row.Close < row.MA20) or (row.MA20 < row.MA50) or (row.MA50 < row.MA200) or (row.RSI < 48))
            print(row)
            print(minStoch, srow['%K'], minMACD, srow.MACD)
        if (((minStoch < srow['%K']) and (minStoch < 25) and (minStoch < row['%K'])) or ((minMACD < srow.MACD) and (minMACD < row.MACD))) and (prow.Close < prow.MA20):
            if (not position['UptrendCorrection']):
                position['UptrendCorrection'] = True
                return True
        else:
            position['UptrendCorrection'] = False
        return False
    except:
        position['UptrendCorrection'] = False
        return False

def isDowntrendCorrection(df, i, position):
    try:
        row = df.loc[i]
        prow = df.loc[i+1]
        srow = df.loc[i+9]
        if (row.Close > row.MA20) or (row.MA20 > row.MA50) or (row.MA50 > row.MA200) or (row.RSI > 52):
            # position['DowntrendCorrection'] = False
            return False
        maxMACD = max(list(df.loc[0:10].MACD))
        maxStoch = max(list(df.loc[0:10]['%K']))
        if (((maxStoch > srow['%K']) and (maxStoch > 75) and (maxStoch > row['%K'])) or ((maxMACD > srow.MACD) and (maxMACD > row.MACD))) and (df.loc[i+1].Close > df.loc[i+1].MA20):
            if (not position['DowntrendCorrection']):
                position['DowntrendCorrection'] = True
                return True
        else:
            position['DowntrendCorrection'] = False
        return False
    except:
        position['DowntrendCorrection'] = False
        return False

def shouldExitLong(df, i, subDf, position):
    row = df.iloc[i]
    newDf = subDf[subDf.Date > row.Date].tail(3)
    for i in reversed(range(len(newDf))):
        if (newDf.iloc[i].Close < newDf.iloc[i].MA20) and (row.MA50 > row.MA200) and (row.MA20 > row.MA50):
            if (not position["ShouldExitLong"]):
                position["UptrendCorrection"] = False
                position["ShouldExitLong"] = True
                return True
        else:
            position["ShouldExitLong"] = False
    return False

def shouldExitShort(df, i, subDf, position):
    row = df.iloc[i]
    newDf = subDf[subDf.Date > row.Date].tail(3)
    for i in reversed(range(len(newDf))):
        if (newDf.iloc[i].Close > newDf.iloc[i].MA20) and (row.MA50 < row.MA200) and (row.MA20 < row.MA50):
            if (not position["ShouldExitShort"]):
                position["DowntrendCorrection"] = False
                position["ShouldExitShort"] = True
                return True
        else:
            position["ShouldExitShort"] = False
    return False

def findPatterns(df, i, subDf, position):
    row = df.loc[i]
    patterns = []
    if isSoftzone(row, position):
        patterns.append("Softzone")
    elif isCrossMA(row, position):
        patterns.append("CrossMA")
    if isUptrendCorrection(df, i, position):
        patterns.append("UptrendCorrection")
    if isDowntrendCorrection(df, i, position):
        patterns.append("DowntrendCorrection")
    if shouldExitLong(df, i, subDf, position):
        patterns.append("ShouldExitLong")
    if shouldExitShort(df, i, subDf, position):
        patterns.append("ShouldExitShort")
    return patterns

def scan():
    stocks = ['VN30F1M', 'VN30F2M']
    positions = pd.read_csv(data_location + os.getenv('positions'))
    message = ""
    patternStocks = []
    foundPatterns = []
    rowIndex = 0
    for stock in stocks:
        logger.info("Scanning {}".format(stock))
        df = pd.read_csv("{}{}_{}.csv".format(intraday, '15', stock))
        subDf = pd.read_csv("{}{}_{}.csv".format(intraday, '5', stock))
        getIndicators(df)
        getIndicators(subDf)
        position = positions[positions.Stock==stock].to_dict(orient='records')[0]
        patterns = findPatterns(df, rowIndex, subDf, position)
        if len(patterns) > 0:
            logger.info(patterns)
            patternStocks.append(stock)
            foundPatterns.append(", ".join(patterns))

    if len(patternStocks) > 0:
        patternDf = pd.DataFrame({"Stock": patternStocks, "Patterns": foundPatterns})
        message = "<H2>{}</H2>\n\n".format(df.iloc[rowIndex].Date)
        sendEmail("PS Pattern Found", message + html_style_basic(patternDf), "html")

def test():
    stocks = ['VN30F1M', 'VN30F2M']
    positions = pd.read_csv(data_location + os.getenv('positions'))
    for col in positions.columns:
        if col != 'Stock':
            positions[col].values[:] = False
    print(positions)
    for stock in stocks:
        print("Test for " + stock)
        df = pd.read_csv("{}{}_{}.csv".format(intraday, '15', stock))
        subDf = pd.read_csv("{}{}_{}.csv".format(intraday, '5', stock))
        position = positions[positions.Stock==stock].to_dict(orient='records')[0]
        print(position)
        getIndicators(df)
        getIndicators(subDf)
        for i in reversed(range(0, (len(df) - 201))):
            patterns = findPatterns(df, i, subDf, position)
            if len(patterns) > 0:
                print(row.Date, ",".join(patterns))
        print(pd.DataFrame([position]))
        

if __name__ == "__main__":
    if sys.argv[1] == 'test':
        logger.info("Test pattern finding")
        test()
    if sys.argv[1] == 'scan':
        logger.info("Realtime finding")
        scan()
