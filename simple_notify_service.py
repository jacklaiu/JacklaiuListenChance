import jqdatasdk
import talib
import numpy as np
import time
import datetime
import util.tools as util
import CollectorPrice.core.mysql2pd as mp
from util.smtpclient import SmtpClient

smtp = SmtpClient(enable=True)

useJqData = True

ma_name = 'EMA'
ema_timeperiods = ['5', '13', '21', '34']
count = 100
start_date = '2019-06-20 00:00:00'
end_dates = []
i = 0
while i < 10:
    d = str(datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=i))
    if util.isFutureTradingTime(d) is True:
        end_dates.append(d)
    i = i + 1

def get_price(security, frequency, end_date, count):
    df = None
    if useJqData is True:
        try:
            jqdatasdk.auth('13268108673', 'king20110713')
            df = jqdatasdk.get_price(security=security, end_date=end_date, count=count, frequency=frequency)
        except Exception as e:
            pass
            # print(e)
    else:
        df = mp.getPrice(security=security,
                         end_date=end_date,
                         count=count,
                         frequency=frequency)
    return df
def getPreDay(end_date):
    df = get_price(security='RB8888.XSGE',
                     end_date=end_date,
                     count=count,
                     frequency='1d')
    return str(df.index.tolist()[-2])

def maName(index):
    return str(ma_name + ema_timeperiods[index])

def judge(df, security, frequency, end_date, action_notify=True, yesterday_securies=None):
    ret = None
    strRet = None
    try:
        close = [float(x) for x in df['close']]
        idx = 0
        while idx < ema_timeperiods.__len__():
            df[maName(idx)] = talib.EMA(np.array(close), timeperiod=int(ema_timeperiods[idx]))
            idx = idx + 1
        df['RSI'] = talib.RSI(np.array(close), timeperiod=9)
        df = df[df[maName(-1)] == df[maName(-1)]]
        rsis = df['RSI'].tolist()
        lastestRsi = float(rsis[-1])
        lastestMutilPricePosi = getMutilPricePosiArray(df)
        rv_ema_timeperiods = ema_timeperiods[::-1]
        str_lastestMutilPricePosi = "_".join(lastestMutilPricePosi)
        str_ema_timeperiods = "_".join(ema_timeperiods)
        str_rv_ema_timeperiods = "_".join(rv_ema_timeperiods)
        if str_lastestMutilPricePosi == str_ema_timeperiods and lastestRsi > 70:
            if action_notify is True:
                _str = "↑#↑#↑#↑" + end_date + ": " + security + " " + frequency
                if security not in yesterday_securies:
                    _str = "NNNNNNNNNNNNNNNNN!↑#↑#↑#↑" + end_date + ": " + security + " " + frequency
                if "NNNNNN" in _str:
                    strRet = "N_UP_" + security
                    print(_str)
            ret = security
        elif str_lastestMutilPricePosi == str_rv_ema_timeperiods and lastestRsi < 30:
            if action_notify is True:
                _str = "↓#↓#↓#↓" + end_date + ": " + security + " " + frequency
                if security not in yesterday_securies:
                    _str = "NNNNNNNNNNNNNNNNN!↓#↓#↓#↓" + end_date + ": " + security + " " + frequency
                if "NNNNNN" in _str:
                    strRet = "N_DOWN_" + security
                    print(_str)
            ret = security
    except Exception as e:
        pass
        # print(e)
    if yesterday_securies is not None:
        return strRet
    else:
        return ret

def getMutilPricePosiArray(df):
    rel = {}
    prices = []
    retArr = []
    for manum in ema_timeperiods:
        mn = ma_name + str(manum)
        lastPrice = df[mn].tolist()[-1]
        rel[lastPrice] = manum
        prices.append(lastPrice)
    prices.sort(reverse=True)
    for p in prices:
        manum = rel[p]
        retArr.append(manum)
    return retArr

def handle(securities, frequencies, end_date, count, action_notify=True, yesterday_securies=None):
    ret_array = []
    for security in securities:
        for frequency in frequencies:
            df = get_price(security=security,
                                end_date=end_date,
                                count=count,
                                frequency=frequency)
            ret = judge(df, security, frequency, end_date, action_notify, yesterday_securies)
            if ret is not None:
                ret_array.append(ret)
    return ret_array

def tick(nowTimeString=None, testdates=None):
    ss = 'RB8888.XSGE_BU8888.XSGE_HC8888.XSGE_ZN8888.XSGE_AP8888.XZCE_CF8888.XZCE' \
         '_MA8888.XZCE_SF8888.XZCE_SM8888.XZCE_ZC8888.XZCE_JD8888.XDCE_M8888.XDCE_EG8888.XDCE'
    sf = '1d'
    if nowTimeString is not None:
        _end_dates = [nowTimeString]
    else:
        _end_dates = testdates
    securities = ss.split('_')
    frequencies = sf.split('_')
    for end_date in _end_dates:
        preDay = getPreDay(end_date)
        yesterday_securies = handle(securities, frequencies, preDay, count, action_notify=False)
        strs = handle(securities, frequencies, end_date, count, yesterday_securies=yesterday_securies)
        ctn = '\n'.join(strs)
        if ctn == '':
            ctn = '没有内容'
        smtp.sendMail(subject='日线策略报告', content=end_date + ": \n" + ctn)

def daemon_listen():
    smtp.sendMail(subject=util.getYMDHMS() + ': 日线策略监听程序启动', content='Engine Start!')
    while True:
        nowTimeString = util.getYMDHMS()
        if '20:30' in util.getHMS() or '08:00' in util.getHMS():
            if util.isFutureTradingTime(nowTimeString) is True:
                tick(nowTimeString)
            else:
                smtp.sendMail(subject='节假日监听程序运行中', content='Engine running!')
            time.sleep(60 * 60)
        time.sleep(49)

daemon_listen()
# tick(nowTimeString='2019-06-26 00:00:00')