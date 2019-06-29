
import jqdatasdk
import talib
import time
import numpy as np
import util.tools as util
import PriceDataFetcher.core.pd2mysql as p2m

class DataBody(object):

    def __init__(self, security, frequency, jqAc='13268108673', jqPw='king20110713'):
        self.df = None
        self.security = security
        self.frequency = frequency
        self.jqAc = jqAc
        self.jqPw = jqPw
        self._lastaccesstimestampObj = {'lastaccesstimestamp': None, 'lastaccesstimestamp_cus': None}
        self._to0100_securies_str = "ZN"

    def getLastestPrice(self, nowTimeString):
        
        newDf = p2m.getPrice(
            security=self.security,
            count=1,
            end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
            frequency=self.frequency,
            fields=['close']
        )
        newIndex = newDf.index.tolist()[-1]
        price = newDf.loc[newIndex]['close']
        return price

    def getLastestPriceWithFrequency(self, nowTimeString=None, frequency='5m'):
        if self._isNeedRefreshLastPrice(nowTimeString, frequency) is False:
            return None
        return self.getLastestPrice(nowTimeString)

    def refresh(self, nowTimeString=None):
        if self._isNeedRefresh(nowTimeString) is False:
            return False
        newRow = None
        newIndex = None
        if self.df is None:
            try:
                self.df = p2m.getPrice(
                    security=self.security,
                    count=300,
                    end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                    frequency=self.frequency,
                    fields=['close', 'open', 'high', 'low', 'volume']
                )
            except:
                pass
                # smtp.sendMail(subject=self.security + ': refreshAdvancedData初始化数据错误！', content='')
        else:

            try:
                newDf = p2m.getPrice(
                    security=self.security,
                    count=1,
                    end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                    frequency=self.frequency,
                    fields=['close', 'open', 'high', 'low', 'volume']
                )
                newIndex = newDf.index.tolist()[-1]
                newRow = newDf.loc[newIndex]
            except:
                try:
                    time.sleep(5)
                    
                    newDf = p2m.getPrice(
                        security=self.security,
                        count=1,
                        end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                        frequency=self.frequency,
                        fields=['close', 'open', 'high', 'low', 'volume']
                    )
                    newIndex = newDf.index.tolist()[-1]
                    newRow = newDf.loc[newIndex]
                except:
                    pass

        if newIndex in self.df.index.tolist():
            return False
        if newRow is not None:
            self.df.loc[newIndex] = newRow
        # close = [float(x) for x in self.df['close']]
        # self.df['RSI9'] = talib.RSI(np.array(close), timeperiod=9)
        # self.df['EMAF'] = talib.EMA(np.array(close), timeperiod=6)
        # self.df['EMAS'] = talib.EMA(np.array(close), timeperiod=23)
        # self.df['EMA5'] = talib.EMA(np.array(close), timeperiod=5)
        # self.df['EMA10'] = talib.EMA(np.array(close), timeperiod=10)
        self.df.drop([self.df.index.tolist()[0]], inplace=True)
        #print(self.df.index.tolist().__len__())
        #print(nowTimeString + ' - ' + 'Data: '+self.security+' Refreshed!')
        return True


    def _isTradeTime(self, nowTimeString=None):
        pre = self.security[0:2]
        hm = nowTimeString[-8:-3]
        if pre in self._to0100_securies_str:
            if '01:00' <= hm < '09:00' or '10:15' <= hm < '10:30' or '11:30' <= hm < '13:30' or '15:00' <= hm < '21:00':
                return False
            else:
                return True
        elif '00:00' <= hm < '09:00' or '10:15' <= hm < '10:30' or '11:30' <= hm < '13:30' or '15:00' <= hm < '21:00' or '23:00' <= hm <= '23:59':
            return False
        else:
            return True

    def _isFixFrenqucy(self, nowTimeString):
        ts = util.string2timestamp(str(nowTimeString))
        lastaccesstimestamp = self._lastaccesstimestampObj['lastaccesstimestamp']
        if lastaccesstimestamp is None:
            self._lastaccesstimestampObj['lastaccesstimestamp'] = ts
            return True
        elif lastaccesstimestamp is None or (ts - lastaccesstimestamp) > (int(self.frequency[0:-1]) * 58):
            self._lastaccesstimestampObj['lastaccesstimestamp'] = ts
            return True
        else:
            return False

    def _isFixCustomFrenqucy(self, nowTimeString, frequency):
        ts = util.string2timestamp(str(nowTimeString))
        lastaccesstimestamp = self._lastaccesstimestampObj['lastaccesstimestamp_cus']
        if lastaccesstimestamp is None:
            self._lastaccesstimestampObj['lastaccesstimestamp_cus'] = ts
            return True
        elif lastaccesstimestamp is None or (ts - lastaccesstimestamp) > (int(frequency[0:-1]) * 58):
            self._lastaccesstimestampObj['lastaccesstimestamp_cus'] = ts
            return True
        else:
            return False

    def _isNeedRefresh(self, nowTimeString):
        return self._isFixFrenqucy(nowTimeString) and \
               util.isFutureTradingTime(nowTimeString) and \
               self._isTradeTime(nowTimeString)

    def _isNeedRefreshLastPrice(self, nowTimeString, frequency):
        return self._isFixCustomFrenqucy(nowTimeString, frequency) and \
               util.isFutureTradingTime(nowTimeString) and \
               self._isTradeTime(nowTimeString)


