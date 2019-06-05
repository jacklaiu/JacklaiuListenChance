
import jqdatasdk
import talib
import time
import numpy as np
import util.tools as util
from databody import DataBody

class AnalysisBody(object):

    def __init__(self):
        pass

    def rsiIsBetween(self, df, top=65, bottom=35, timeperiod=9):
        close = [float(x) for x in df['close']]
        name = 'RSI' + str(timeperiod)
        df[name] = talib.RSI(np.array(close), timeperiod=timeperiod)
        rsi = df[name][-1]
        newIndex = df.index.tolist()[-1]
        if rsi > top or rsi < bottom:
            return {'ret': False, 'val': rsi, 'idx': newIndex}
        else:
            return {'ret': True, 'val': rsi, 'idx': newIndex}

    def doubleEMALargerThan(self, df, from_timeperiod=6, to_timeperiod=23):
        close = [float(x) for x in df['close']]
        fromname = 'EMA' + str(from_timeperiod)
        toname = 'EMA' + str(to_timeperiod)
        df[fromname] = talib.EMA(np.array(close), timeperiod=from_timeperiod)
        df[toname] = talib.EMA(np.array(close), timeperiod=to_timeperiod)
        lastFromEma = df[fromname][-1]
        lastToEma = df[toname][-1]
        newIndex = df.index.tolist()[-1]
        if lastFromEma > lastToEma:
            return {'ret': True, 'idx': newIndex}
        else:
            return {'ret': False, 'idx': newIndex}






