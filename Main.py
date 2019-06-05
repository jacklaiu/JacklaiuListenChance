# coding: utf-8

import jqdatasdk
import talib
import numpy as np
import time
import util.tools as Util
from util.smtpclient import SmtpClient as smtp

pa_ledge = 10
lastaccesstimestampObj = {'lastaccesstimestamp': None}

frequency = '13m'
dfMap = {}
resultMap = {}
preTimeMap = {}
securities = ['RB8888.XSGE']
test_starttime = '2019-03-10 23:50:00'
rsi_top = 70
rsi_bottom = 30
scount_top = 2200

time_duration = 12 * 60 * 60

to0100_securies_str = 'ZN'

def result(security, scount, paup, padw, nowTimeString, rsi, pricePosi):
    if security in resultMap:
        obj = resultMap[security]
        _scount = obj['scount']
        _paup = obj['paup']
        _padw = obj['padw']
        _pricePosi = obj['pricePosi']
        _ymd = obj['timepoint'][0:9]
        ymd = nowTimeString[0:9]
        if _ymd == ymd:
            return
        if (_paup != paup) or (_padw != padw):
            resultMap[security] = {'scount': scount, 'paup': paup, 'padw': padw, 'timepoint': nowTimeString, 'rsi': rsi, 'pricePosi': pricePosi}
            print(str(scount) + "=@@@=" + nowTimeString + ' - ' + security + ' -paup: ' + str(paup) + ' -padw: ' + str(
                padw) + ' -rsi: ' + str(rsi))
    else:
        resultMap[security] = {'scount': scount, 'paup': paup, 'padw': padw, 'timepoint': nowTimeString, 'rsi': rsi, 'pricePosi': pricePosi}
        print(str(scount) + "=@@@=" + nowTimeString + ' - ' + security + ' -paup: ' + str(paup) + ' -padw: ' + str(
            padw) + ' -rsi: ' + str(rsi))

def refreshAdvancedData(security, nowTimeString=None):
    jqdatasdk.auth('13268108673', 'king20110713')
    newRow = None
    newIndex = None
    df = None
    if dfMap is None:
        exit()
    if security not in dfMap.keys():
        dfMap.setdefault(security, df)
    else:
        df = dfMap.get(security)

    if df is None:
        try:
            df = jqdatasdk.get_price(
                security=security,
                count=300,
                end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                frequency=frequency,
                fields=['close', 'open', 'high', 'low', 'volume']
            )
        except:
            smtp.sendMail(subject=security + ': refreshAdvancedData初始化数据错误！', content='')
    else:
        try:
            newDf = jqdatasdk.get_price(
                security=security,
                count=1,
                end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                frequency=frequency,
                fields=['close', 'open', 'high', 'low', 'volume']
            )
            newIndex = newDf.index.tolist()[0]
            newRow = newDf.loc[newIndex]
        except:
            try:
                time.sleep(5)
                jqdatasdk.auth('13268108673', 'king20110713')
                newDf = jqdatasdk.get_price(
                    security=security,
                    count=1,
                    end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                    frequency=frequency,
                    fields=['close', 'open', 'high', 'low', 'volume']
                )
                newIndex = newDf.index.tolist()[0]
                newRow = newDf.loc[newIndex]
            except:
                pass

    if newRow is not None:
        df.loc[newIndex] = newRow
    close = [float(x) for x in df['close']]
    df['RSI9'] = talib.RSI(np.array(close), timeperiod=9)
    df['EMAF'] = talib.EMA(np.array(close), timeperiod=6)
    df['EMAS'] = talib.EMA(np.array(close), timeperiod=23)
    df.drop([df.index.tolist()[0]], inplace=True)
    dfMap[security] = df

def getVolumeArrow(df, indexList):
    count = 0
    i = indexList.__len__() - 1
    flagVolume = df.loc[indexList[i], 'volume']
    i = i - 1
    while i >= 0:
        volume = df.loc[indexList[i], 'volume']
        if flagVolume > volume:
            count = count + 1
        else:
            break
        i = i - 1
    return count

def getStatusChangeCount(df):
    pricePosis = getPricePosiArray(df)
    i = pricePosis.__len__() - 1
    count = 0
    while i >= 1:
        posi = pricePosis[i]
        if posi == pricePosis[i-1]:
            count = count + 1
        else:
            break
        i = i - 1
    return count


def getPricePosiArray(df):
    indexList = df[df.EMAS == df.EMAS].index.tolist()
    pricePositions = []
    for index in indexList:
        emafast = df.loc[index, 'EMAF']
        emas = sorted(
            # [ema5, self.df.loc[index, 'EMA10'], self.df.loc[index, 'EMA20'], self.df.loc[index, 'EMA40'], self.df.loc[index, 'EMA60']],
            [emafast, df.loc[index, 'EMAS']],
            reverse=True)
        pricePosi = 0
        for ema in emas:
            if ema == emafast:
                break
            pricePosi = pricePosi + 1
        pricePositions.append(pricePosi)
    return pricePositions

def getPriceArrowUp(df, indexList):
    count = 0
    i = indexList.__len__() - 1
    closeFlag = df.loc[indexList[i], 'close']
    i = i - 1
    while i >= 0:
        close = df.loc[indexList[i], 'close']
        if closeFlag > close:
            count = count + 1
        else:
            break
        i = i - 1
    return count

def getPriceArrowDown(df, indexList):
    count = 0
    i = indexList.__len__() - 1
    closeFlag = df.loc[indexList[i], 'close']
    i = i - 1
    while i >= 0:
        close = df.loc[indexList[i], 'close']
        if closeFlag < close:
            count = count + 1
        else:
            break
        i = i - 1
    return count

def isTradeTime(security=None, nowTimeString=None):
    pre = security[0:2]
    hm = nowTimeString[-8:-3]
    if pre in to0100_securies_str:
        if '01:00' <= hm < '09:00' or '10:15' <= hm < '10:30' or '11:30' <= hm < '13:30' or '15:00' <= hm < '21:00':
            return False
        else:
            return True
    elif '00:00' <= hm < '09:00' or '10:15' <= hm < '10:30' or '11:30' <= hm < '13:30' or '15:00' <= hm < '21:00' or '23:00' <= hm <= '23:59':
        return False
    else:
        return True

def markPreTimepoint(security, nowTimeString):
    if security in preTimeMap.keys():
        map = preTimeMap[security]
        map['timepoint'] = nowTimeString
    else:
        map = {'timepoint': nowTimeString}
        preTimeMap[security] = map

def isNextRound(security, nowTimeString):
    if security not in preTimeMap.keys():
        return True
    preTimepoint = preTimeMap[security]['timepoint']
    sec = Util.diff_time_second(nowTimeString, preTimepoint)
    if sec > time_duration:
        return True
    return False

def notify(security, nowTimeString):
    if security in dfMap.keys():
        df = dfMap[security]
        if df is None:
            return
        indexList = df.index.tolist()
        #vac = getVolumeArrow(df=df, indexList=indexList)
        paup = getPriceArrowUp(df=df, indexList=indexList)
        padw = getPriceArrowDown(df=df, indexList=indexList)
        pricePosis = getPricePosiArray(df)
        scount = getStatusChangeCount(df)
        lastestIndex = indexList[-1]
        rsi = df.loc[lastestIndex, 'RSI9']

        if (rsi > rsi_top or rsi < rsi_bottom) and (paup > pa_ledge or padw > pa_ledge) and isNextRound(security, nowTimeString) is True and scount < scount_top:
            print(nowTimeString + ' - ' + security + ' -paup: ' + str(paup) + ' -padw: ' + str(padw) + ' -rsi: ' + str(rsi) + ' -scount: ' + str(scount))
            markPreTimepoint(security, nowTimeString)

        # if int(paup) > pa_ledge and int(rsi) > rsi_top and scount < 30:
        #     result(security, scount, paup, padw, nowTimeString, rsi, pricePosi=pricePosis[-1])
        # if int(padw) > pa_ledge and int(rsi) < rsi_bottom and scount < 30:
        #     result(security, scount, paup, padw, nowTimeString, rsi, pricePosi=pricePosis[-1])

def loop(nowTimeString):
    ts = Util.string2timestamp(str(nowTimeString))
    lastaccesstimestamp = lastaccesstimestampObj['lastaccesstimestamp']
    if lastaccesstimestamp is None:
        lastaccesstimestampObj['lastaccesstimestamp'] = ts
    if lastaccesstimestamp is None or (ts - lastaccesstimestamp) > (int(frequency[0:-1]) * 58):
        for security in securities:
            if isTradeTime(security=security, nowTimeString=nowTimeString) is False:
                continue
            refreshAdvancedData(security=security, nowTimeString=nowTimeString)
            notify(security, nowTimeString)
            lastaccesstimestampObj['lastaccesstimestamp'] = ts

def main():
    while True:
        nowTimeString = Util.getYMDHMS()
        if Util.isFutureTradingTime(nowTimeString=nowTimeString) is False:
            time.sleep(58)
            continue
        loop(nowTimeString=nowTimeString)
        time.sleep(4)

def test():
    ts = Util.getTimeSerial(starttime=test_starttime, count=100000, periodSec=58)
    for nowTimeString in ts:
        if Util.isFutureTradingTime(nowTimeString=nowTimeString) is False:
            continue
        loop(nowTimeString)

test()
