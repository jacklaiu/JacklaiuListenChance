import jqdatasdk
import talib
import numpy as np
import util.tools as tools

def check(securitys, frequencys, nowTimeString=tools.getYMDHMS()):
    strArray = []
    jqdatasdk.auth('13268108673', 'king20110713')
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
            df['EMAF'] = talib.EMA(np.array(close), timeperiod=6)
            df['EMAS'] = talib.EMA(np.array(close), timeperiod=23)
            count = getPricePosiArrayDur(df)
            rsi = df[df.EMAS == df.EMAS].RSI9.tolist()[-1]
            row += "#frequency:" + f + "_count:" + str(count) + "_rsi:" + str(rsi)
            print('[' + tools.getYMDHMS() + ']: ' + nowTimeString + ' - ' + s + ' - ' + f + ' - ' + str(count) + ' - ' + str(rsi))
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

], ['1d', '120m', '60m'], '2019-06-11 12:30:00')

print("\n".join(strArray))

rowStr = ""
for row in strArray:
    skipRow = False
    cols = row.split('##')
    security = cols[0].split(':')[-1][0:2]
    frequencyRows = cols[-1].split('#')
    rowmsg = [security]
    counts = []
    for fr in frequencyRows:
        frequency = fr.split('_')[0].split(':')[1]
        count = int(fr.split('_')[1].split(':')[1])
        rsi = float(fr.split('_')[2].split(':')[1])
        if count > 0 and rsi < 65:
            skipRow = True
            break
        if count < 0 and rsi > 35:
            skipRow = True
            break
        rowmsg.append(str(count))
        counts.append(count)

    if skipRow is True:
        continue
    num = 0
    if counts.__len__() == frequencyRows.__len__():
        for c in counts:
            if c >= 5:
                num = num + 1
        if num == counts.__len__():
            continue

    rowStr = rowStr + "_".join(rowmsg) + "\n"

print(rowStr)

