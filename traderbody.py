
import jqdatasdk
import talib
import time
import numpy as np
import util.tools as util
from databody import DataBody
from analysisbody import AnalysisBody

class TraderBody(object):

    def __init__(self, security, frequency, starttime_fortest, endtime_fortest=util.getYMDHMS(),
                 layer1_from_timeperiod=5, layer1_to_timeperiod=10,
                 layer1_rsi_top=65, layer1_rsi_bottom=35, layer1_rsi_timeperiod=9):
        self.db = DataBody(security, frequency)
        self.ab = AnalysisBody()
        self.ownPosition = 0
        self.starttime_fortest = starttime_fortest
        self.endtime_fortest = endtime_fortest
        # 策略层次1
        self.layer1_from_timeperiod = layer1_from_timeperiod
        self.layer1_to_timeperiod = layer1_to_timeperiod
        self.layer1_rsi_top = layer1_rsi_top
        self.layer1_rsi_bottom = layer1_rsi_bottom
        self.layer1_rsi_timeperiod = layer1_rsi_timeperiod
        self.layer1_pre1_ownerPosition = None
        self.layer1_ownPosition = 0
        self.layer1_startcount = 0
        self.layer1_startRate = 0
        self.layer1_pre_flag_5IsLt10 = False
        self.layer1_rates = []
        self.layer1_starttime_rate_map = {}

    # return: buy - sell ||| short - cover
    def getAction(self, nowTimeString):
        refreshed = self.db.refresh(nowTimeString)
        if refreshed is False:
            return
        self.layer1()

    def layer1(self):
        ret_5IsLt10 = self.ab.doubleEMALargerThan(df=self.db.df, from_timeperiod=self.layer1_from_timeperiod, to_timeperiod=self.layer1_to_timeperiod)
        flag_5IsLt10 = ret_5IsLt10['ret']
        ret_rsi9_active = self.ab.rsiIsBetween(df=self.db.df, top=self.layer1_rsi_top, bottom=self.layer1_rsi_bottom, timeperiod=self.layer1_rsi_timeperiod)
        flag_rsi9_active = ret_rsi9_active['ret'] is not True
        if flag_5IsLt10 is True and flag_rsi9_active is True and str(self.layer1_ownPosition) == '0':
            # mark pre
            self.layer1_pre1_ownerPosition = self.layer1_ownPosition
            # change posi
            self.layer1_ownPosition = 1
            self.layer1_startcount = 0
            self.layer1_startRate = 0
            self.layer1_pre_flag_5IsLt10 = True
            nowTimeString = str(self.db.df.index.tolist()[-1])
            print('duo start: ' + nowTimeString)

        elif flag_5IsLt10 is False and flag_rsi9_active is True and str(self.layer1_ownPosition) == '0':
            # mark pre
            self.layer1_pre1_ownerPosition = self.layer1_ownPosition
            # change posi
            self.layer1_ownPosition = -1
            self.layer1_startcount = 0
            self.layer1_startRate = 0
            self.layer1_pre_flag_5IsLt10 = False
            nowTimeString = str(self.db.df.index.tolist()[-1])
            print('kon start: ' + nowTimeString)

        elif str(self.layer1_ownPosition) != '0' and self.layer1_pre_flag_5IsLt10 != flag_5IsLt10:
            ######################################################################
            self.layer1_startcount = self.layer1_startcount + 1
            startDf = self.db.df[-self.layer1_startcount - 1:-self.layer1_startcount]
            closeDf = self.db.df[-1:]
            startClose = startDf.iloc[0]['close']
            endClose = closeDf.iloc[0]['close']
            if self.layer1_ownPosition > 0:
                self.layer1_startRate = (1 + round((endClose - startClose) / startClose, 4))
            else:
                self.layer1_startRate = (1 + round((startClose - endClose) / startClose, 4))
            nowTimeString = str(self.db.df.index.tolist()[-1])
            print("!!!!!!!!!!!!!!!!!" + nowTimeString + " ownerPosition: " + str(self.layer1_ownPosition)
                  + " startCount: " + str(self.layer1_startcount)
                  + " startRate: " + str(self.layer1_startRate))
            self.layer1_rates.append(self.layer1_startRate)
            self.layer1_starttime_rate_map[nowTimeString] = self.layer1_startRate
            ######################################################################
            # mark pre
            self.layer1_pre1_ownerPosition = self.layer1_ownPosition
            # change posi
            self.layer1_ownPosition = 0
            self.layer1_startcount = 0
            self.layer1_startRate = 0

        else:
            self.layer1_startcount = self.layer1_startcount + 1
            indexes = self.db.df.index.tolist()
            startDf = self.db.df[-self.layer1_startcount-1:-self.layer1_startcount]
            closeDf = self.db.df[-1:]
            startClose = startDf.iloc[0]['close']
            endClose = closeDf.iloc[0]['close']
            self.layer1_startRate = (1 + round((endClose - startClose)/startClose, 4))

        # nowTimeString = str(self.db.df.index.tolist()[-1])
        # print(nowTimeString + " ownerPosition: " + str(self.layer1_ownPosition)
        #       + " startCount: " + str(self.layer1_startcount)
        #       + " startRate: " + str(self.layer1_startRate))


    def testMain(self):
        if self.starttime_fortest is None:
            return
        ts = util.getTimeSerial(starttime=self.starttime_fortest, periodSec=59, count=300000)
        for nowTimeString in ts:
            if nowTimeString > self.endtime_fortest:
                return
            action = self.getAction(nowTimeString)
            if action == 'buy':
                pass
            if action == 'sell':
                pass
            if action == 'short':
                pass
            if action == 'cover':
                pass


ft = 5
tt = 10
rt = 65
rb = 35
rtp = 9
trader = TraderBody(security='HC8888.XSGE', frequency='17m', starttime_fortest='2019-01-01 22:00:00',
                    layer1_from_timeperiod=ft, layer1_to_timeperiod=tt,
                    layer1_rsi_top=rt, layer1_rsi_bottom=rb, layer1_rsi_timeperiod=rtp)
trader.testMain()
total_rate = 1
for r in trader.layer1_rates:
    total_rate = total_rate * r
print(total_rate)

items = sorted(trader.layer1_starttime_rate_map.items(), key=lambda x: x[1], reverse=True)
for item in items:
    print(item)

