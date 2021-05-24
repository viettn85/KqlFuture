
import os 
from ingestContracts import retrieveContracts
from updateTrades import getTransactions
from scanBigBoys import analyze
import datetime
import traceback
from dotenv import load_dotenv
load_dotenv(dotenv_path='future.env')
import pandas as pd
import schedule
import time

def job():
    today = datetime.date.today().strftime("%Y-%m-%d")
    getTransactions(os.getenv('contractStock'), today)
    try:
        contracts = analyze(os.getenv('contractStock'), today)
    except:
        print("Waiting for traced transactions...")
        contracts = []
    currentContracts = []
    try:
        currentContracts = pd.read_csv("{}{}.csv".format(os.getenv('contract_trades'), today))
    except Exception:
        print('First time run on {}'.format(today))
    if len(contracts) > len(currentContracts):
        print(len(contracts), len(currentContracts))
        os.system('say "Big Boys! Attention"')
        contracts.to_csv("{}{}.csv".format(os.getenv('contract_trades'), today), index=False)

if __name__ == '__main__':
    schedule.every(10).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
