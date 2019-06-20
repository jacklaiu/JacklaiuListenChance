import jqdatasdk
import talib
import time
import numpy as np
import util.tools as tools
from util.smtpclient import SmtpClient

smtpClient = SmtpClient()


def check(securitys, frequencys, nowTimeString=tools.getYMDHMS()):
    strArray = []
    try:
        jqdatasdk.auth('13268108673', 'king20110713')
    except:
        smtpClient.sendMail(subject="JQdatasdk认证失败", content='JQdatasdk认证失败')
    print('[' + tools.getYMDHMS() + ']: start checking')
    for s in securitys:
        row = "security:" + s + "#"
        for f in frequencys:
            print('[' + tools.getYMDHMS() + ']: start handling security - ' + str(s) + ' frequency - ' + str(f))
            df = jqdatasdk.get_price(
                security=s,
                count=50,
                end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                frequency=f,
                fields=['close', 'open', 'high', 'low', 'volume']
            )
            close = [float(x) for x in df['close']]
            df['RSI9'] = talib.RSI(np.array(close), timeperiod=9)
            df['EMAF'] = talib.EMA(np.array(close), timeperiod=5)
            df['EMAS'] = talib.EMA(np.array(close), timeperiod=16)
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
            if posi != 1:
                count = -count
            break
    return count


def action(nowTimeString):
    strArray = check([
        'RB9999.XSGE',
        'BU9999.XSGE',
        'HC9999.XSGE',
        'ZN9999.XSGE',
        'AP9999.XZCE',
        'CF9999.XZCE',
        'MA9999.XZCE',
        'SF9999.XZCE',
        'SM9999.XZCE',
        'ZC9999.XZCE',
        'JD9999.XDCE',
        'M9999.XDCE',
        'EG9999.XDCE'
    ], ['1d', '120m', '60m'], nowTimeString)
    print("\n".join(strArray))
    rowStr = ""
    for row in strArray:
        skipRow = False
        cols = row.split('##')
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
                if count1 == 0 and (abs(c) > 5 or (c > 0 and rsi < 65) or (c < 0 and rsi > 35)):
                    break
                if abs(c) >= 5:
                    num = num + 1
                count1 = count1 + 1
            if num == counts.__len__() or count1 == 0:
                continue
        if rowmsg.__len__() > 0:
            rowStr = rowStr + "_".join(rowmsg) + "\n"
        else:
            rowStr = "正在搜寻机会..."

    print(rowStr)
    smtpClient.sendMail(subject="[" + nowTimeString + "]: 机会报告", content=rowStr)


def startListen():
    while True:
        nowTimeString = tools.getYMDHMS()
        if tools.isFutureTradingTime(nowTimeString) is False or tools.isOpen(nowTimeString) is False:
            time.sleep(61)
            continue
        hms = tools.getHMS()
        tick = False
        if "08:00:00" < hms < "08:01:00" or "10:00:00" < hms < "10:01:00" or "12:30:00" < hms < "12:31:00" or "14:00:00" < hms < "14:01:00" or "20:30:00" < hms < "20:31:00" or "22:00:00" < hms < "22:01:00":
            tick = True
        if tick is False:
            time.sleep(50)
            print("[" + nowTimeString + "]: tick is False")
            continue
        time.sleep(61)
        print("[" + nowTimeString + "]: action")
        action(nowTimeString)


startListen()
# action("2019-06-13 08:00:00")
