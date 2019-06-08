
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
                 layer1_rsi_top=65, layer1_rsi_bottom=35, layer1_rsi_timeperiod=9, layer2_stoprate=0.01):
        self.security = security
        self.frequency = frequency
        self.db = DataBody(security, frequency)
        self.ab = AnalysisBody()
        self.ownPosition = 0
        self.starttime_fortest = starttime_fortest
        self.endtime_fortest = endtime_fortest
        self.rates_markAtHandleAction = []
        self.actions_markAtHandleAction = ['']

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
        self.layer1_action = None
        # 策略层次2
        self.layer2_stoprate = layer2_stoprate
        self.layer2_nowPrice = None
        self.layer2_maxRate = 0
        self.layer2_nowRate = 0
        self.layer2_action = None

        self.smtpClient = SmtpClient()

    # return: buy - sell ||| short - cover
    def layer2(self, nowTimeString):
        if self.layer1_startprice > 0:
            self.layer2_nowPrice = self.db.getLastestPrice(nowTimeString)
        # 已收市@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if self.layer2_nowPrice is None:
            self.layer2_nowRate = None
            return
        if self.layer1_startprice > 0 and self.layer2_nowPrice > 0:
            if self.layer1_ownPosition > 0:
                self.layer2_nowRate = (1 + round((self.layer2_nowPrice - self.layer1_startprice) / self.layer1_startprice, 4))
            else:
                self.layer2_nowRate = (1 + round((self.layer1_startprice - self.layer2_nowPrice) / self.layer1_startprice, 4))

        # 记录最近最大rate
        if self.layer2_nowRate is not None and self.layer2_nowRate > 0:
            if self.layer2_maxRate is None or self.layer2_maxRate == 0 and self.layer1_action != 'clear':
                self.layer2_maxRate = self.layer2_nowRate
            else:
                if self.layer2_nowRate is not None and self.layer2_nowRate > self.layer2_maxRate and self.layer1_action != 'clear':
                    self.layer2_maxRate = self.layer2_nowRate

        if self.layer2_nowRate is not None and self.layer2_nowRate > 0:
            print("[" + nowTimeString + "]: nowRate - " + str(self.layer2_nowRate) + " | maxRate - " + str(
                self.layer2_maxRate) + " | distance - " + str(self.layer2_maxRate - self.layer2_nowRate))
            # 排除这波已经发出stop的情况，避免重复stop
            preAction = self.actions_markAtHandleAction[-1]
            if preAction != 'clear' and preAction != 'stop' and (self.layer2_maxRate - self.layer2_nowRate) > self.layer2_stoprate:
                self.layer2_action = 'stop'

    def layer1(self, nowTimeString=None):
        refreshed = self.db.refresh(nowTimeString)
        if refreshed is False:
            return
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
            lastIndex = self.db.df.index.tolist()[-1]
            self.layer1_startprice = self.db.df.loc[lastIndex]['close']

            self.layer1_action = 'duo'

        elif flag_5IsLt10 is False and flag_rsi9_active is True and str(self.layer1_ownPosition) == '0':
            # mark pre
            self.layer1_pre1_ownerPosition = self.layer1_ownPosition
            # change posi
            self.layer1_ownPosition = -1
            self.layer1_startcount = 0
            self.layer1_startRate = 0
            self.layer1_pre_flag_5IsLt10 = False
            lastIndex = self.db.df.index.tolist()[-1]
            self.layer1_startprice = self.db.df.loc[lastIndex]['close']

            self.layer1_action = 'kon'

        elif str(self.layer1_ownPosition) != '0' and self.layer1_pre_flag_5IsLt10 != flag_5IsLt10:
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
            self.layer1_rates.append(self.layer1_startRate)
            self.layer1_starttime_rate_map[nowTimeString] = self.layer1_startRate
            # mark pre
            self.layer1_pre1_ownerPosition = self.layer1_ownPosition
            # change posi
            self.layer1_ownPosition = 0
            self.layer1_startcount = 0
            self.layer1_startRate = 0
            self.layer1_startprice = 0
            self.layer2_maxRate = 0
            # self.layer2_nowRate = 0
            self.layer2_nowPrice = 0

            self.layer1_action = 'clear'

        else:
            self.layer1_startcount = self.layer1_startcount + 1
            # startDf = self.db.df[-self.layer1_startcount-1:-self.layer1_startcount]
            # closeDf = self.db.df[-1:]
            # startClose = startDf.iloc[0]['close']
            # endClose = closeDf.iloc[0]['close']
            # self.layer1_startRate = (1 + round((endClose - startClose)/startClose, 4))
            self.layer1_action = 'still'

    def handleAction(self, nowTimeString):
        # layer1 动作处理 #################################################
        preAction = self.actions_markAtHandleAction[-1]
        if self.layer1_action == 'duo':
            print('Action duo [' + nowTimeString + ']: ' + str(self.layer1_action))
            self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 多。",
                                     content='请手动开仓并设置止损线。', receivers='jacklaiu@163.com')
        elif self.layer1_action == 'kon':
            print('Action kon [' + nowTimeString + ']: ' + str(self.layer1_action))
            self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 空。",
                                     content='请手动开仓并设置止损线。', receivers='jacklaiu@163.com')
        elif self.layer1_action == 'clear':
            print('Action clear [' + nowTimeString + ']: ' + str(self.layer1_action))
            self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 结束持仓提示。",
                                     content='如未清仓请手动操作。',
                                     receivers='jacklaiu@163.com')
            # 如果这波交易已经stop了就不要在记录多一次了
            if preAction != 'stop':
                self.rates_markAtHandleAction.append(self.layer2_nowRate)
                self.layer2_nowRate = 0
            print('###################rates_markAtHandleAction: ' + str(self.rates_markAtHandleAction))

        elif self.layer1_action == 'still':
            pass

        # layer2 动作处理 #################################################
        elif self.layer2_action == 'stop':
            print('Action stop [' + nowTimeString + ']: ' + str(self.layer1_action))
            self.smtpClient.sendMail(subject="[" + self.frequency + "]" + self.security + ": 中途结束持仓提示。",
                                     content='如未清仓请手动操作。',
                                     receivers='jacklaiu@163.com')
            self.rates_markAtHandleAction.append(self.layer2_nowRate)
            self.layer2_nowRate = 0

        # 动作日志
        if self.layer1_action is not None and self.layer1_action != '' and self.layer1_action != 'still':
            self.actions_markAtHandleAction.append(self.layer1_action)
        if self.layer2_action is not None and self.layer2_action != '' and self.layer2_action != 'still':
            self.actions_markAtHandleAction.append(self.layer2_action)
        # 每次动作处理过后，要清理layer_action变量，这个变量一次有效
        self.layer1_action = ''
        self.layer2_action = ''

    def testMain(self):
        if self.starttime_fortest is None:
            return
        ts = util.getTimeSerial(starttime=self.starttime_fortest, periodSec=59, count=300000)
        now = util.getYMDHMS()
        for nowTimeString in ts:
            self.tick(nowTimeString)
            if nowTimeString > now or nowTimeString > self.endtime_fortest:
                return

    def tick(self, nowTimeString=util.getYMDHMS()):
        self.layer1(nowTimeString)
        self.layer2(nowTimeString)
        self.handleAction(nowTimeString)

ft = 5
tt = 10
rt = 65
rb = 35
rtp = 9
layer2_stoprate = 0.005
trader = TraderBody(security='RB8888.XSGE', frequency='16m',
                    starttime_fortest='2019-03-28 22:00:00',
                    endtime_fortest='2019-04-09 22:00:00',
                    layer1_from_timeperiod=ft, layer1_to_timeperiod=tt,
                    layer1_rsi_top=rt, layer1_rsi_bottom=rb, layer1_rsi_timeperiod=rtp,
                    layer2_stoprate=layer2_stoprate)
trader.testMain()
total_rate = 1
for r in trader.rates_markAtHandleAction:
    total_rate = total_rate * r
print(total_rate)

print("layer2_stoprate: " + str(layer2_stoprate))

# items = sorted(trader.layer1_starttime_rate_map.items(), key=lambda x: x[1], reverse=True)
# for item in items:
#     print(item)

