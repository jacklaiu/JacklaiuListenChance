
import jqdatasdk
import talib
import time
import numpy as np
import util.tools as util
from databody import DataBody
from analysisbody import AnalysisBody
from util.smtpclient import SmtpClient

class TraderBody(object):

    def __init__(self, security, frequency, starttime_fortest=None, endtime_fortest=util.getYMDHMS(),
                 layer1_from_timeperiod=5, layer1_to_timeperiod=10,
                 layer1_rsi_top=65, layer1_rsi_bottom=35, layer1_rsi_timeperiod=9):
        self.security = security
        self.frequency = frequency
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
        self.layer1_startprice = 0
        self.layer1_startRate = 0
        self.layer1_pre_flag_5IsLt10 = False
        self.layer1_rates = []
        self.layer1_starttime_rate_map = {}
        # 策略层次2
        self.layer2_nowPrice = None

        self.smtpClient = SmtpClient()

    # return: buy - sell ||| short - cover
    def getAction(self, nowTimeString):
        refreshed = self.db.refresh(nowTimeString)
        if refreshed is False:
            return
        return self.layer1()

    def layer2(self):
        pass

    def layer1(self):
        ret_5IsLt10 = self.ab.doubleEMALargerThan(df=self.db.df, from_timeperiod=self.layer1_from_timeperiod, to_timeperiod=self.layer1_to_timeperiod)
        flag_5IsLt10 = ret_5IsLt10['ret']
        ret_rsi9_active = self.ab.rsiIsBetween(df=self.db.df, top=self.layer1_rsi_top, bottom=self.layer1_rsi_bottom, timeperiod=self.layer1_rsi_timeperiod)
        # print(ret_rsi9_active['val'])
        flag_rsi9_active = ret_rsi9_active['ret'] is not True
        if flag_5IsLt10 is True and flag_rsi9_active is True and str(self.layer1_ownPosition) == '0':
            # mark pre
            self.layer1_pre1_ownerPosition = self.layer1_ownPosition
            # change posi
            self.layer1_ownPosition = 1
            self.layer1_startcount = 0
            self.layer1_startRate = 0
            self.layer1_pre_flag_5IsLt10 = True
            lastIndex = self.db.df.index.tolist()[-1]
            nowTimeString = str(lastIndex)
            self.layer1_startprice = self.db.df.loc[lastIndex]['close']
            # print('duo start: ' + nowTimeString)
            # self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 多。",
            #                          content='请手动开仓并设置止损线。', receivers='jacklaiu@163.com')
            return 'duo'

        elif flag_5IsLt10 is False and flag_rsi9_active is True and str(self.layer1_ownPosition) == '0':
            # mark pre
            self.layer1_pre1_ownerPosition = self.layer1_ownPosition
            # change posi
            self.layer1_ownPosition = -1
            self.layer1_startcount = 0
            self.layer1_startRate = 0
            self.layer1_pre_flag_5IsLt10 = False
            lastIndex = self.db.df.index.tolist()[-1]
            nowTimeString = str(lastIndex)
            self.layer1_startprice = self.db.df.loc[lastIndex]['close']
            # print('kon start: ' + nowTimeString)
            # self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 空。",
            #                          content='请手动开仓并设置止损线。',
            #                          receivers='jacklaiu@163.com')
            return 'kon'

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
            # print("end trade: " + nowTimeString + " ownerPosition: " + str(self.layer1_ownPosition)
            #       + " startCount: " + str(self.layer1_startcount)
            #       + " startRate: " + str(self.layer1_startRate))
            # self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 结束持仓提示。",
            #                          content='如未清仓请手动操作。',
            #                          receivers='jacklaiu@163.com')
            #print("\n")
            self.layer1_rates.append(self.layer1_startRate)
            self.layer1_starttime_rate_map[nowTimeString] = self.layer1_startRate
            ######################################################################
            # mark pre
            self.layer1_pre1_ownerPosition = self.layer1_ownPosition
            # change posi
            self.layer1_ownPosition = 0
            self.layer1_startcount = 0
            self.layer1_startRate = 0
            self.layer1_startprice = 0
            return 'clear'

        else:
            self.layer1_startcount = self.layer1_startcount + 1
            indexes = self.db.df.index.tolist()
            startDf = self.db.df[-self.layer1_startcount-1:-self.layer1_startcount]
            closeDf = self.db.df[-1:]
            startClose = startDf.iloc[0]['close']
            endClose = closeDf.iloc[0]['close']
            self.layer1_startRate = (1 + round((endClose - startClose)/startClose, 4))

            return 'still'

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
            self.layer2_nowPrice = self.db.getLastestPrice(nowTimeString)
            action = self.getAction(nowTimeString)
            if action == 'duo':
                print('[' + nowTimeString + ']: ' + str(action))
                self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 多。",
                                         content='请手动开仓并设置止损线。', receivers='jacklaiu@163.com')
            if action == 'kon':
                print('[' + nowTimeString + ']: ' + str(action))
                self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 空。",
                                         content='请手动开仓并设置止损线。', receivers='jacklaiu@163.com')
            if action == 'clear':
                print('[' + nowTimeString + ']: ' + str(action))
                self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 结束持仓提示。",
                                         content='如未清仓请手动操作。',
                                         receivers='jacklaiu@163.com')
            if action == 'still':
                nowRate = 0
                if self.layer1_startprice > 0 and self.layer2_nowPrice > 0:
                    if self.layer1_ownPosition > 0:
                        nowRate = (1 + round((self.layer2_nowPrice - self.layer1_startprice) / self.layer1_startprice, 4))
                    else:
                        nowRate = (1 + round((self.layer1_startprice - self.layer2_nowPrice) / self.layer1_startprice, 4))

                print('[' + nowTimeString + ']: ' + str(action) + " -> " + str(nowRate))

    def tick(self):
        nowTimeString = util.getYMDHMS()
        self.layer2_nowPrice = self.db.getLastestPrice(nowTimeString)
        action = self.getAction(nowTimeString)
        if action == 'duo':
            print('[' + nowTimeString + ']: ' + str(action))
            self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 多。",
                                     content='请手动开仓并设置止损线。', receivers='jacklaiu@163.com')
        if action == 'kon':
            print('[' + nowTimeString + ']: ' + str(action))
            self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 空。",
                                     content='请手动开仓并设置止损线。', receivers='jacklaiu@163.com')
        if action == 'clear':
            print('[' + nowTimeString + ']: ' + str(action))
            self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 结束持仓提示。",
                                     content='如未清仓请手动操作。',
                                     receivers='jacklaiu@163.com')
        if action == 'still':
            nowRate = 0
            if self.layer1_startprice > 0 and self.layer2_nowPrice > 0:
                if self.layer1_ownPosition > 0:
                    nowRate = (1 + round((self.layer2_nowPrice - self.layer1_startprice) / self.layer1_startprice, 4))
                else:
                    nowRate = (1 + round((self.layer1_startprice - self.layer2_nowPrice) / self.layer1_startprice, 4))

            print('[' + nowTimeString + ']: ' + str(action) + " -> " + str(nowRate))


# ft = 5
# tt = 10
# rt = 65
# rb = 35
# rtp = 9
# trader = TraderBody(security='RB8888.XSGE', frequency='15m', starttime_fortest='2019-05-23 09:00:00',
#                     layer1_from_timeperiod=ft, layer1_to_timeperiod=tt,
#                     layer1_rsi_top=rt, layer1_rsi_bottom=rb, layer1_rsi_timeperiod=rtp)
# trader.testMain()
# total_rate = 1
# for r in trader.layer1_rates:
#     total_rate = total_rate * r
# print(total_rate)
#
# items = sorted(trader.layer1_starttime_rate_map.items(), key=lambda x: x[1], reverse=True)
# for item in items:
#     print(item)

