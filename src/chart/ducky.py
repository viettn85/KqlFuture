import sys, os
sys.path.append('src/util')
import pandas as pd
import numpy as np
import mplfinance as fplt
from utils import *
from dotenv import load_dotenv
import shutil

load_dotenv(dotenv_path='stock.env')
np.seterr(divide='ignore', invalid='ignore')
data_location = os.getenv("data")
intraday = data_location + os.getenv("intraday")
location = os.getenv("images")

def draw(stock, timeframe):
    df = pd.read_csv("{}{}_{}.csv".format(intraday, timeframe, stock), parse_dates=True)
    getIndicators(df)
    df.index = pd.DatetimeIndex(df['Date'])
    df['ADX20'] = 20
    df['RSI70'] = 70
    df['RSI30'] = 30
    df['Stoch20'] = 20
    df['Stoch80'] = 80
    df['MACD0'] = 0
    df = df[0:100]
    df.sort_index(ascending=True, inplace=True)
    
    
    mc = fplt.make_marketcolors(
                            up='tab:blue',down='tab:red',
                            volume='inherit',
    )
    apds = [ fplt.make_addplot(df['MA20'], panel=0,color='red'),
                fplt.make_addplot(df['MA50'], panel=0,color='blue'),
                fplt.make_addplot(df['MA200'], panel=0,color='green'),
                fplt.make_addplot(df['Volume'], type = 'line', linestyle=' ', panel =1, mav = 20, color='g'),
                fplt.make_addplot(df['MACD'], panel=2,color='blue'),
                fplt.make_addplot(df['MACD_SIGNAL'], panel=2,color='red'),
                fplt.make_addplot(df['MACD0'], panel=2,color='grey'),
                fplt.make_addplot(df['%K'], panel=3, color='red'),
                fplt.make_addplot(df['%D'], panel=3,color='blue'),
                fplt.make_addplot(df['Stoch20'], panel=3,color='grey'),
                fplt.make_addplot(df['Stoch80'], panel=3,color='grey'),
                fplt.make_addplot(df['RSI'], panel=4,color='red'),
                fplt.make_addplot(df['RSI70'], panel=4,color='grey'),
                fplt.make_addplot(df['RSI30'], panel=4,color='grey'),
                fplt.make_addplot(df['ADX'], panel=5,color='blue'),
                fplt.make_addplot(df['PDI'], panel=5,color='green'),
                fplt.make_addplot(df['NDI'], panel=5,color='red'),
                fplt.make_addplot(df.ADX20, type = 'line', panel=5,color='grey')
                ]
    # s  = fplt.make_mpf_style(base_mpl_style="seaborn", y_on_right=True, marketcolors=mc, mavcolors=["red","orange","skyblue"])
    s  = fplt.make_mpf_style(base_mpl_style="seaborn", y_on_right=True, marketcolors=mc)
    fplt.plot(
                df,
                type='candle',
                style=s,
                title="{} - {}".format(stock, timeframe),
                ylabel='',
                # mav=(20, 50, 200),
                volume=True,
                addplot=apds,
                savefig=dict(fname='{}{}_{}.png'.format(location, stock, timeframe),dpi=100,pad_inches=0.25)
    )

import cufflinks as cf
import chart_studio.plotly as py

cf.set_config_file(theme='pearl',sharing='public',offline=True)
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
# import cufflinks as cf
# init_notebook_mode()

def exportAll():
    stocks = ['VN30', 'VN30F1M', 'VN30F2M', "VNINDEX"]
    timeframes = ['5', '15', '60', 'D']
    for stock in stocks:
        for timeframe in timeframes:
            draw(stock, timeframe)

def drawQuant(stock):
    df = pd.read_csv("{}{}.csv".format(data_realtime, stock), index_col="Date", parse_dates=True)[0:300]
    # df.sort_index(ascending=True, inplace=True)
    qf=cf.QuantFig(df,title='Apple Quant Figure',legend='top',name='GS', asImage=True, display_image=True)
    qf.add_bollinger_bands()
    qf.add_volume()
    # qf.iplot(asImage=True)
    py.image.save_as(qf.iplot(), 'scatter_plot', format='png')

if __name__ == "__main__":
    exportAll()
