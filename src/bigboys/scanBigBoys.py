import os
import sys
from datetime import datetime
import requests
import pandas as pd
import numpy as np

from dotenv import load_dotenv
load_dotenv(dotenv_path='future.env')

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()


def analyze(stock, date):
    contracts = pd.read_csv(os.getenv('contract_data') + date + "-" + stock + ".csv")
    contracts = contracts[(contracts.Type == "B") | (contracts.Type == "S")]
    volumes = contracts.Volume
    outliers = detect_outlier(volumes)
    
    logger.info("There are {} Big Boy's trades".format(len(outliers)))
    # minOutlier = min(outliers)
    minOutlier = 100
    contracts = contracts[contracts.Volume >= minOutlier]
    print(contracts.head(10))
    return contracts

def detect_outlier(data):
    outliers = []
    threshold=3
    mean_1 = np.mean(data)
    std_1 =np.std(data)
    for y in data:
        z_score= (y - mean_1)/std_1 
        if np.abs(z_score) > threshold:
            outliers.append(y)
    return outliers


if __name__ == '__main__':
    analyze(os.getenv('contractStock'), sys.argv[1])
