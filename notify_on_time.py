import jqdatasdk
import talib
import time
import numpy as np
import util.tools as tools
from util.smtpclient import SmtpClient
import PriceDataFetcher.util.pd2mysql as p2m

smtpClient = SmtpClient()

frequencyArr = ['60m', '30m', '10m']
testTimePoint = '2019-06-13 08:00:00'


def getListenForwardShakeUrl(security):
    data = "security:" + security + "_frequency:60m"
    return "http://localhost:64211/lfs?data=" + data

def check(securitys, frequencys, nowTimeString=tools.getYMDHMS()):
    strArray = []
    print('[' + tools.getYMDHMS() + ']: start checking')
    for s in securitys:
        row = "security:" + s + "#"
        for f in frequencys:
            print('[' + tools.getYMDHMS() + ']: start handling security - ' + str(s) + ' frequency - ' + str(f))
            df = p2m.getPrice(
                security=s,
                count=50,
                end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                frequency=f,
                fields=['close', 'open', 'high', 'low', 'volume']
            )
            close = [float(x) for x in df['close']]
            df['RSI9'] = talib.RSI(np.array(close), timeperiod=9)
            df['EMAF'] = talib.EMA(np.array(close), timeperiod=5)
            df['EMAS'] = talib.EMA(np.array(close), timeperiod=10)
            count = getPricePosiArrayDur(df)
            rsi = df[df.EMAS == df.EMAS].RSI9.tolist()[-1]
            row += "#frequency:" + f + "_count:" + str(count) + "_rsi:" + str(rsi)
            print('[' + tools.getYMDHMS() + ']: ' + nowTimeString + ' - ' + s + ' - ' + f + ' - ' + str(
                count) + ' - ' + str(rsi))
        strArray.append(row)
    return strArray


def getPricePosiArrayDur(df):
    indexList = df[df.EMAS == df.EMAS].index.tolist()
    pricePositions = []
    for index in indexList:
        emafast = df.loc[index, 'EMAF']
        emas = sorted(
            [emafast, df.loc[index, 'EMAS']],
            reverse=True)
        pricePosi = 0
        for ema in emas:
            if ema == emafast:
                break
            pricePosi = pricePosi + 1
        pricePositions.append(pricePosi)
        # print(str(index) + " :" + str(pricePosi))
    lastestPosi = None
    count = 0
    pricePositions.reverse()
    for posi in pricePositions:
        if lastestPosi is None:
            lastestPosi = posi
            continue
        if lastestPosi == posi:
            count = count + 1
        else:
            if lastestPosi != 0:
                count = -count
            break
    return count


def action(nowTimeString=tools.getYMDHMS()):
    strArray = check([
        'RB8888.XSGE',
        'BU8888.XSGE',
        'HC8888.XSGE',
        'ZN8888.XSGE',
        'AP8888.XZCE',
        'CF8888.XZCE',
        'MA8888.XZCE',
        'SF8888.XZCE',
        'SM8888.XZCE',
        'ZC8888.XZCE',
        'JD8888.XDCE',
        'M8888.XDCE',
        'EG8888.XDCE'
    ], frequencyArr, nowTimeString)
    print("\n".join(strArray))
    rowStr = ""
    rowHtml = ""
    for row in strArray:
        skipRow = False
        cols = row.split('##')
        realSecurity = cols[0].split(':')[-1]
        security = cols[0].split(':')[-1][0:2]
        frequencyRows = cols[-1].split('#')
        rowmsg = [security]
        counts = []
        rsis = []
        for fr in frequencyRows:
            frequency = fr.split('_')[0].split(':')[1]
            count = int(fr.split('_')[1].split(':')[1])
            rsi = float(fr.split('_')[2].split(':')[1])
            # if count > 0 and rsi < 65:
            #     skipRow = True
            #     break
            # if count < 0 and rsi > 35:
            #     skipRow = True
            #     break
            rowmsg.append(str(count))
            counts.append(count)
            rsis.append(rsi)

        if skipRow is True:
            continue
        num = 0
        if counts.__len__() == frequencyRows.__len__():
            count1 = 0
            for c in counts:
                rsi = rsis[count1]
                if count1 == 0 and (abs(c) > 5 or (c > 0 and rsi < 60) or (c < 0 and rsi > 40)):
                    break
                if abs(c) >= 5:
                    num = num + 1
                count1 = count1 + 1
            if num == counts.__len__() or count1 == 0:
                continue
        if rowmsg.__len__() > 0:
            rowHtml = rowHtml + '<a href="'+getListenForwardShakeUrl(realSecurity)+'">' + "_".join(rowmsg) + "</a><br/>"
            rowStr = rowStr + "_".join(rowmsg) + '\n'
        else:
            rowHtml = "正在搜寻机会..."

    rowHtml = rowHtml + '\n' + str("Frequencies: " + "_".join(frequencyArr))
    print(rowStr)
    print(rowHtml)
    smtpClient.sendMail(subject="[" + nowTimeString + "]: 机会报告", content=rowHtml)


def startListen():
    while True:
        nowTimeString = tools.getYMDHMS()
        if tools.isFutureTradingTime(nowTimeString) is False or tools.isOpen(nowTimeString) is False:
            time.sleep(61)
            continue
        hms = tools.getHMS()
        tick = False
        if "08:00:00" < hms < "08:01:00" or \
                "10:00:00" < hms < "10:01:00" or \
                "12:30:00" < hms < "12:31:00" or \
                "14:00:00" < hms < "14:01:00" or \
                "20:30:00" < hms < "20:31:00" or \
                "22:00:00" < hms < "22:01:00":
            tick = True
        if tick is False:
            time.sleep(50)
            print("[" + nowTimeString + "]: tick is False")
            continue
        time.sleep(61)
        print("[" + nowTimeString + "]: action")
        action(nowTimeString)

# startListen()
action(testTimePoint)
