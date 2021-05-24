import os
import sys
from datetime import datetime

import requests
import pandas as pd
import numpy as np

from dotenv import load_dotenv
load_dotenv(dotenv_path='contract.env')

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

from contractUtils import getEpoch, getDatetime

def convertTime(t):
    datetimes = list(map(lambda x: getDatetime(x), t))
    dates = list(map(lambda x: x[0:10], datetimes))
    times = list(map(lambda x: x[11:], datetimes))
    return (dates, times)

def etl(data):
    (dates, times) = convertTime(data['t'])
    return pd.DataFrame.from_dict({
        'Date': dates,
        'Time': times,
        'Open': data['o'],
        'Close': data['c'],
        'High': data['h'],
        'Low': data['l'],
        'Volume': data['v']
    })

def save(df, stock, fromDate, toDate):
    logger.info("Saving trades of {} from {} to {}".format(stock, fromDate, toDate))
    dates = pd.date_range(fromDate, toDate).tolist()
    for date in dates:
        dateStr =  date.strftime("%Y-%m-%d")
        dateDf = df[df.Date == dateStr]
        if len(dateDf) > 0:
            dateDf.to_csv(os.getenv('contract_intraday') + dateStr + "-" + stock + ".csv", index=False)
    df.to_csv(os.getenv('contract_intraday') + stock + ".csv", index=False)

def retrieveContracts(stock, fromDate, toDate):
    # https://plus24.mbs.com.vn/tradingview/api/1.1/history?symbol=VN30F2010&resolution=1&from=1602054018&to=1602147678
    logger.info("Ingesting trades of {} from {} to {}".format(stock, fromDate, toDate))
    PARAMS = {
                'symbol': stock,
                'resolution': os.getenv('resolution'),
                'from': getEpoch(fromDate),
                'to': getEpoch(toDate)
            }
    data = requests.get(url=os.getenv('historyUrl'), params=PARAMS).json()
    save(etl(data), stock, fromDate, toDate)

if __name__ == '__main__':
    retrieveContracts(os.getenv('contractStock'), sys.argv[1], sys.argv[2])

