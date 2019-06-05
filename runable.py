
import jqdatasdk
import talib
import time
import numpy as np
import util.tools as util
from databody import DataBody
from analysisbody import AnalysisBody

ts = util.getTimeSerial(starttime='2019-04-01 10:00:00', periodSec=59, count=20000)
db = DataBody(security='RB8888.XSGE', frequency='30m')
ab = AnalysisBody()
for nowTimeString in ts:
    flag = db.refresh(nowTimeString)
    if flag is True:
        print("###############" + nowTimeString
              + " - rsi9: " + str(ab.rsiIsBetween(db.df)['val'])
              + " - rsiIsBetween: " + str(ab.rsiIsBetween(db.df)['ret'])
              + " - largeThan: " + str(ab.doubleEMALargerThan(db.df)['ret']))
