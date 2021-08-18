import sys
sys.path.append('src/chart')
sys.path.append('src/crawler')

from ducky import *
from realtime import *

if __name__ == '__main__':
    crawlRecentIntraday()
    exportAll()
