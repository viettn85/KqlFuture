import os
import sys
import pandas as pd
from datetime import datetime
import requests
import traceback

import logging
import logging.config
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

from dotenv import load_dotenv
load_dotenv(dotenv_path='future.env')

PIN = os.getenv('pinf')
COOKIE = os.getenv('cookief')

def generateParams(orderType, orderVolume, orderPrice, ordtype, stopOrderType, stopPrice):
    return {
        'accountNo': '266453D',
        'orderPin': PIN,
        'refOrderId': '',
        'traderId': '',
        'channel': '',
        'symbol': os.getenv('contractStock'),
        'tradeBy': 'Q',
        'tradeByValue': 0,
        'position': 'O',
        'side': orderType,
        'price': orderPrice,
        'conPrice': '',
        'stopPrice': stopPrice,
        'volume': orderVolume,
        'minVolume': 0,
        'validity': '',
        'validityDate': datetime.today().strftime("%Y%m%d") + '-',
        'toler': 0,
        'auctionOrder': 0,
        'remark': '',
        'ordtype': ordtype,
        'stopOrderType': stopOrderType,
        'pegOffsetValue': '',
        'pegMoveType': '',
        'pageOffsetType': '',
        'pegLimitType': '',
        'isSavePin': 0,
        'authenId': ''
    }

def getPrice(contract):
    try:
        params = {
            'regId': '0_FO_FOS_TF_SQ',
            'seqhose': -1,
            'seqhnx': -1,
            'sequpcom': -1,
            'stocklist': contract,
            'currentFav': 'ASCVN30',
            'priceboardType': 'PriceboardIntraday',
            'marketName': 'VN30'
        }
        headers = {'Content-type': 'application/x-www-form-urlencoded; charset=utf-8', 'cookie': COOKIE}
        r = requests.post(os.getenv('priceUrl'), params=params, data=None, headers=headers)
        if r.text == "":
            return (-1, -1, -1)
        else:
            data = r.json()['HOSE'][0][0]
            return (data[8], data[10], data[13])
    except:
        traceback.print_exc()
        logger.error('Error to get prices')
        return ()

def order(orderType, orderVolume, orderPrice, ordtype, stopOrderType, stopPrice):
    logger.info("Test")
    params = generateParams(orderType, orderVolume, orderPrice, ordtype, stopOrderType, stopPrice)
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=utf-8', 'cookie': COOKIE}
    r = requests.post(os.getenv('orderUrl'), params=params, data=None, headers=headers)
    displayErrorMsg(r)
    logger.info("The new order ID: {}".format(r.json()['Result']['OrderId']))

def cancel(orderId):
    params = {
        'accountNo': '266453D',
        'targetCustomerID': '266453',
        'orderPin': PIN,
        'refOrderId': '',
        'orderId': orderId,
        'channel': '',
        'remark': '',
        'isSavePin': 1,
        'authenId': '',
        'caData': ''
    }
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=utf-8', 'cookie': COOKIE}
    r = requests.post(os.getenv('cancelUrl'), params=params, data=None, headers=headers)
    displayErrorMsg(r)
    logger.info("You canceled order Id: {}".format(r.json()['Result'][0]['OrderId']))

def listOrder():
    params = {
        'accountNo': '266453D',
        'market': 'VN',
        'exchange': 'F',
        'symbol': '',
        'conPrice': 'X',
        'side': '',
        'channelId': '',
        'listcond': 'pending,false|matched,false|semi,false|cancelling,false|cancelled,false|rejected,false|expired,false',
        'orderId': -1,
        'canCancel': 0,
        'pageIndex': 1,
        'pageSize': 10
    }
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=utf-8', 'cookie': COOKIE}
    r = requests.post(os.getenv('listOrderUrl'), params=params, data=None, headers=headers)
    errorMsg = r.json()['errorMsg']
    if (errorMsg != ""):
        logger.info(r.json()['errorMsg'])
    logger.info("There are {} orders".format(len(r.json()['Result'])))
    if len(r.json()['Result']) > 0:
        orders = []
        df = pd.DataFrame()
        for order in r.json()['Result']:
            detail = {
                'ID': [order['ID']],
                'OrderStatus': [order['OrderStatus']],
                'Side': [order['Side']],
                'SecSymbol': [order['SecSymbol']],
                'Price': [order['Price']],
                'Volume': [order['Volume']],
                # 'ConPrice': [order['ConPrice']],
                'StatusText': [order['StatusText']],
                'OrderStatus': [order['OrderStatus']],
                'StopPrice': [order['StopPrice']],
                # 'Position': [order['Position']],
                'TransTime': [order['TransTime']],
                'OrderTypeName': [order['OrderTypeName']],
                # 'StopOrderTypeName': [order['StopOrderTypeName']],
                # 'OrderType': [order['OrderType']]
            }
            df = df.append(pd.DataFrame.from_dict(detail))
        logger.info(df)

def orderDetails(orderId, volume, price, conditionPrice):
    params = {
        'accountNo': '266453D',
        'market': 'VN',
        'exchange': 'F',
        'symbol': '',
        'conPrice': 'X',
        'side': '',
        'channelId': '',
        'listcond': 'pending,false|matched,false|semi,false|cancelling,false|cancelled,false|rejected,false|expired,false',
        'orderId': -1,
        'canCancel': 0,
        'pageIndex': 1,
        'pageSize': 10
    }
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=utf-8', 'cookie': COOKIE}
    r = requests.post(os.getenv('listOrderUrl'), params=params, data=None, headers=headers)
    if len(r.json()['Result']) > 0:
        orders = []
        df = pd.DataFrame()
        for order in r.json()['Result']:
            if str(order['ID']) != orderId:
                continue
            params = {
                'orderId': orderId,
                'orderPin': PIN,
                'refOrderId': '',
                'symbol': order['SecSymbol'],
                'volume': volume,
                'price': price,
                'conPrice': '',
                'side': order['Side'],
                'accountNo': order['Account'],
                'auctionOrder': 0,
                'traderId': '',
                'channel': '',
                'remark': '',
                'stopPrice': conditionPrice,
                'validityDate': '20201222-',
                'ordtype': order['OrderType'],
                'stopOrderType': order['StopOrderType'],
                'pegOffsetValue': '',
                'pegMoveType': '',
                'pageOffsetType': '',
                'pegLimitType': '',
                'isSavePin': 0,
                'authenId': '',
                'caData': ''
            }
            # print(order)
            r = requests.post(os.getenv('changeUrl'), params=params, data=None, headers=headers)
            # print(r.json())
            displayErrorMsg(r)
            logger.info("New order ID: {}".format(r.json()['Result']['OrderId']))

def listPositions():
    params = {
        'tabIndex': 'OP',
        'accountNo': '266453D',
        'fromDate': '',
        'toDate': '20201101',
        'side': '',
        'pageIndex': 1,
        'pageSize': 10
    }
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=utf-8', 'cookie': COOKIE}
    r = requests.post(os.getenv('listPositionUrl'), params=params, data=None, headers=headers)
    displayErrorMsg(r)
    logger.info("There are {} open positions".format(len(r.json()['Result']['OpenPosition'])))
    if len(r.json()['Result']['OpenPosition']) > 0:
        logger.info(r.json()['Result']['OpenPosition'])

def displayErrorMsg(r):
    errorMsg = r.json()['errorMsg']
    if (errorMsg != ""):
        logger.info(r.json()['errorMsg'])

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'orders':
            listOrder()
        if sys.argv[1] == 'positions':
            listPositions()
    prices = getPrice(os.getenv('contractStock'))
    logger.info("The current prices: {}".format(prices))
    if len(sys.argv) == 3:
        if sys.argv[1] == 'cancel':
            cancel(sys.argv[2])
            sys.exit(1)
        if (prices[0] == -1):
            logger.info("Authetication Error")
            sys.exit(1)
        if (prices[0] == 0):
            logger.info("The current system price is not set")
            sys.exit(1)
        if sys.argv[1] == 'buy':
            price = prices[2]
            order("B", sys.argv[2], price, 0, 0, 0)
            logger.info("Buy {} at {}".format(sys.argv[2], price))
        if sys.argv[1] == 'sell':
            price = prices[0]
            order("S", sys.argv[2], price, 0, 0, 0)
            logger.info("Sell {} at {}".format(sys.argv[2], price))
    if len(sys.argv) == 4:
        price = sys.argv[3]
        if sys.argv[1] == 'buy':
            order("B", sys.argv[2], price, 0, 0, 0)
            logger.info("Buy {} at {}".format(sys.argv[2], price))
        if sys.argv[1] == 'sell':
            order("S", sys.argv[2], price, 0, 0, 0)
            logger.info("Sell {} at {}".format(sys.argv[2], price))
    if sys.argv[1] == 'update':
            logger.info("Updating...")
            orderDetails(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            sys.exit(1)
    if len(sys.argv) == 6:
        logger.info("Condition")
        side = ""
        stopOrderType = -1
        price = sys.argv[3]
        if sys.argv[1] == 'buy':
            side = "B"
        if sys.argv[1] == 'sell':
            side = "S"
        if sys.argv[1] == 'buy':
            side = "B"
        if sys.argv[4] == 'up':
            stopOrderType = 3
        if sys.argv[4] == 'down':
            stopOrderType = 4
        if sys.argv[4] == 'tup':
            stopOrderType = 5
        if sys.argv[4] == 'tdown':
            stopOrderType = 6
        if (side != "") & (stopOrderType != -1):
            logger.info(side + " " + str(stopOrderType))
        logger.info(side)
        logger.info(stopOrderType)

        order(side, sys.argv[2], price, 1, stopOrderType, sys.argv[5])