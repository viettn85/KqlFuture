from datetime import datetime
import pytz
from pytz import timezone

def getEpoch(date, time=""):
    lastTime = date + " "
    if time == "":
        time = "09:00:00"
    if len(time) == 5: # 22:29
        time = time + ":00"
    lastTime = lastTime + time
    vntz = timezone('Asia/Ho_Chi_Minh')
    dateObj = datetime.strptime(lastTime, '%Y-%m-%d %H:%M:%S')
    loc_dt = vntz.localize(dateObj)
    return (int)(loc_dt.timestamp())

def getMillisec(date, time=""):
    return getEpoch(date, time) * 1000

def getDatetime(epoch):
    # return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
    return datetime.fromtimestamp(epoch, tz= pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')

# print(getEpoch('2020-10-07', '14:01:00'))
# print(getDatetime(1602054060))