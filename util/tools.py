# coding: utf-8
import tushare as ts
import time
import json
import jqdatasdk
import datetime
from chinese_calendar import is_workday  # , is_holiday
import os
# 没有夜盘
str_no_night = 'jd_ap_v8_v9_sm_sf_l9_l8'
# 23:00就收市
str_no_2330 = 'rb'

def acJQ_StockName(security):
    pre0 = security[0:3]
    pre1 = security[0:2]
    if security.__len__() > 6 and 'SH' in security:
        return security
    if '30' == pre1 or '002' == pre0 or '000' == pre0 or '00' == pre1:
        return security + '.XSHE'
    else:
        return security + '.XSHG'

def isStock(security):
    if '.' in security:
        xchg = security[-4:]
        if xchg == 'XSHG' or xchg == 'XSHE':
            return True
        return False
    else:
        if '002' in security or '60' in security or '000' in security or '30' in security:
            return True
        else:
            return False

def log(words=''):
    ymd = getYMD()
    f = open('log_' + ymd, 'a')
    f.write(words + "\n")
    f.close()

def clearProperties():
    f = open('properties.txt', 'w')
    f.write('')
    f.close()

def removeProperty(key):
    f = open('properties.txt', 'r')
    ctn = f.read()
    f.close()
    if ctn is None or ctn == '':
        return
    else:
        propertiesObj = json.loads(ctn)
    v = propertiesObj.get(key)
    if v is None or v == '':
        return
    del propertiesObj[key]
    ctn = json.dumps(propertiesObj)
    f = open('properties.txt', 'w')
    f.write(ctn)
    f.close()


def setProperty(key, value):
    f = open('properties.txt', 'r')
    ctn = f.read()
    f.close()
    if ctn is None or ctn == '' or ctn == '{}':
        propertiesObj = {}
    else:
        propertiesObj = json.loads(ctn)
        if key in propertiesObj:
            del propertiesObj[key]
    propertiesObj.setdefault(key, value)
    ctn = json.dumps(propertiesObj)
    f = open('properties.txt', 'w')
    f.write(ctn)
    f.close()

def hset(key, field, value):
    obj = getProperty(key)
    if obj is None:
        obj = {field: value}
        setProperty(key, obj)
    else :
        obj.setdefault(field, value)
        setProperty(key, obj)

def hget(key, field):
    obj = getProperty(key)
    if obj is None:
        return None
    else:
        return obj.get(field)

def hdel(key, field):
    obj = {}
    # obj = getProperty(key)
    if obj is None:
        return
    else:
        if field in obj:
            del obj[field]
        setProperty(key, obj)

def getProperty(key):
    f = open('properties.txt', 'r')
    ctn = f.read()
    if ctn is None or ctn == '':
        propertiesObj = {}
    else:
        propertiesObj = json.loads(ctn)
    return propertiesObj.get(key)

def get_dominant_future(jqSecurityName=None, jqSecurityXChg=None, jqDataAccount='13268108673', jqDataPassword='king20110713'):
    jqdatasdk.auth(jqDataAccount, jqDataPassword)
    str = jqSecurityName + '8888.' + jqSecurityXChg
    ret = jqdatasdk.get_dominant_future(str, getYMD())
    if ret == '':
        ret = jqdatasdk.get_dominant_future('RB9999.XSGE', getYMD())
    return ret

def get_CTA_Format_name(securityName=None):
    if securityName is None or securityName == '':
        return
    originSN = securityName
    securityName = securityName.upper()[0:2]
    line = 'EG.XDCE_AG.XSGE_PB.XSGE_AU.XSGE_RB.XSGE_AL.XSGE_RU.XSGE_BU.XSGE_SN.XSGE_CU.XSGE_WR.XSGE_FU.XSGE_ZN.XSGE_HC.XSGE_NI.XSGE_CY.XZCE_RM.XZCE_CF.XZCE_RM.XZCE_FG.XZCE_RS.XZCE_JR.XZCE_SF.XZCE_LR.XZCE_SM.XZCE_MA.XZCE_SR.XZCE_TA.XZCE_OI.XZCE_PM.XZCE_ZC.XZCE_AP.XZCE_JD.XDCE_JM.XDCE_BB.XDCE_M8.XDCE_CS.XDCE_P8.XDCE_FB.XDCE_PP.XDCE_I1.XDCE_V1.XDCE_J1.XDCE_Y1.XDCE_A1.XDCE_B1.XDCE_L1.XDCE_C1.XDCE_M1.XDCE_P1.XDCE_I2.XDCE_V2.XDCE_J2.XDCE_Y2.XDCE_A2.XDCE_B2.XDCE_L2.XDCE_C2.XDCE_M2.XDCE_P2.XDCE'
    list = line.split('_')
    for el in list:
        if securityName in el:
            strs = el.split('.')
            name = strs[0]
            if securityName.__len__() != name.__len__():
                continue
            xchg = strs[1]
            isxzce = xchg == 'XZCE'
            isxsge = xchg == 'XSGE'
            isxdce = xchg == 'XDCE'
            if isxzce is True:
                str = originSN
                str = str[0:2].upper() + str[-3:] + '.CZCE'
                return str
            if isxsge is True:
                str = originSN
                str = str[0:2].lower() + str[-4:] + '.SHFE'
                return str
            if isxdce is True:
                str = originSN
                if str[1:2] in '123456789':
                    str = str[0:1].lower() + str[-4:] + '.DCE'
                else:
                    str = str[0:2].lower() + str[-4:] + '.DCE'
                return str

def get_JQ_Format_name(securityName=None):
    if securityName is None or securityName == '':
        return
    originSN = securityName
    securityName = securityName.upper()[0:2]
    line = 'EG.XDCE_AG.XSGE_PB.XSGE_AU.XSGE_RB.XSGE_AL.XSGE_RU.XSGE_BU.XSGE_SN.XSGE_CU.XSGE_WR.XSGE_FU.XSGE_ZN.XSGE_HC.XSGE_NI.XSGE_CY.XZCE_RM.XZCE_CF.XZCE_RM.XZCE_FG.XZCE_RS.XZCE_JR.XZCE_SF.XZCE_LR.XZCE_SM.XZCE_MA.XZCE_SR.XZCE_TA.XZCE_OI.XZCE_PM.XZCE_ZC.XZCE_AP.XZCE_JD.XDCE_JM.XDCE_BB.XDCE_M8.XDCE_CS.XDCE_P8.XDCE_FB.XDCE_PP.XDCE_I1.XDCE_V1.XDCE_J1.XDCE_Y1.XDCE_A1.XDCE_B1.XDCE_L1.XDCE_C1.XDCE_M1.XDCE_P1.XDCE_I2.XDCE_V2.XDCE_J2.XDCE_Y2.XDCE_A2.XDCE_B2.XDCE_L2.XDCE_C2.XDCE_M2.XDCE_P2.XDCE'
    list = line.split('_')
    for el in list:
        if securityName in el:
            strs = el.split('.')
            name = strs[0]
            if securityName.__len__() != name.__len__():
                continue
            xchg = strs[1]
            isxzce = xchg == 'XZCE'
            isxsge = xchg == 'XSGE'
            isxdce = xchg == 'XDCE'
            if isxzce is True:
                str = originSN
                str = str[0:6].upper() + '.XZCE'
                return str
            if isxsge is True:
                str = originSN
                str = str[0:6].upper() + '.XSGE'
                return str
            if isxdce is True:
                str = originSN
                if str[1:2] in '123456789':
                    str = str[0:5].upper() + '.XDCE'
                else:
                    str = str[0:6].upper() + '.XDCE'
                return str

def futureName(security):
    os = security
    security = security[0:2].lower()
    rel = {'rb': '螺纹', 'bu': '沥青', 'ru': '橡胶', 'fu': '燃油', 'hc': '热卷',
           'cy': '棉纱', 'cf': '棉花', 'rm': '菜籽', 'ma': '甲醇', 'ta': 'PTA', 'zc': '郑煤',
           'a8': '豆一', 'b8': '豆二', 'jm': '焦煤', 'm8': '豆粕'}
    ret = rel.get(security)
    if ret is None:
        return os
    else:
        return ret


def shouldClearPositionNow(nowTimeString=None, security=None):
    now = datetime.datetime.strptime(nowTimeString, "%Y-%m-%d %H:%M:%S")
    # 判断是否大于2日的假期，因为大于2日的假期，最后一天晚上交易所下班了
    isTorrowLongHoildayBegin = False
    count = 0
    while count < 3:
        date = now + datetime.timedelta(days=1)
        if is_workday(date) is True:
            break
        if count == 2:
            isTorrowLongHoildayBegin = True
        count = count + 1

    pre = None
    if security is not None:
        pre = security[0:2].lower()
    str = (now + datetime.timedelta(minutes=2)).strftime("%H:%M")

    if isTorrowLongHoildayBegin is True and str == '15:00':
        return True
    if pre in str_no_night and str == '15:00':
        return True
    if pre in str_no_2330 and str == '23:00':
        return True
    if str == '23:00':
        return True
    return False


def shouldResetPositionNow(security=None):
    str = (datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%H:%M")
    if str == '09:01':
        return True
    return False


# 公用期货日内交易时间
def isFutureCommonTradingTime(nowTimeString=None, security=None):
    s0 = '09:00:00'
    e0 = '10:15:00'
    s1 = '10:30:00'
    e1 = '11:30:00'
    s2 = '13:30:00'
    e2 = '15:00:00'
    s3 = '21:00:00'
    e3 = '23:00:00'
    hms = nowTimeString
    date = None
    isTorrowLongHoildayBegin = False
    if nowTimeString.__len__() > 10:
        datestr = nowTimeString[0:10]
        datestrs = datestr.split('-')
        date = datetime.date(int(datestrs[0]), int(datestrs[1]), int(datestrs[2]))
        hms = nowTimeString[11:nowTimeString.__len__()]

    if date is not None:
        # 判断是否大于2日的假期，因为大于2日的假期，最后一天晚上交易所下班了
        count = 0
        while count < 3:
            date = date + datetime.timedelta(days=1)
            if is_workday(date) is True:
                break
            if count == 2:
                isTorrowLongHoildayBegin = True
            count = count + 1

    pre = None
    if security is not None:
        pre = security[0:2].lower()

    if pre is not None and pre in str_no_night:
        if hms > s0 and hms < e0:
            return True
        if hms > s1 and hms < e1:
            return True
        if hms > s2 and hms < e2:
            return True
    elif pre is not None and pre in str_no_2330:
        if hms > s0 and hms < e0:
            return True
        if hms > s1 and hms < e1:
            return True
        if hms > s2 and hms < e2:
            return True
        if hms > s3 and hms < '23:00:00' and isTorrowLongHoildayBegin is False:
            return True
    else:
        if hms > s0 and hms < e0:
            return True
        if hms > s1 and hms < e1:
            return True
        if hms > s2 and hms < e2:
            return True
        if hms > s3 and hms < e3 and isTorrowLongHoildayBegin is False:
            return True
    return False


def getJSONFromFile(filepath):
    f = open(filepath, 'r')
    str = f.read()
    if str is None or str == '':
        return None
    jsonObject = json.loads(s=str, encoding="UTF-8")
    return jsonObject


def isFutureTradingTime(nowTimeString):
    wd = weekday(nowTimeString=nowTimeString)
    # 排除周末
    if wd == 5 or wd == 6:
        return False
    return True


# 0-6 周一到周日
def weekday(nowTimeString):
    return datetime.datetime.strptime(nowTimeString, "%Y-%m-%d %H:%M:%S").weekday()


# 获取时间序列
def getTimeSerial(starttime, count, periodSec):
    ts = string2timestamp(starttime)
    list = []
    while count > 0:
        ts = ts + periodSec
        list.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)))
        count = count - 1
    return list

def getTimeSerialBySecurity(starttime, count, periodSec, security):
    ts = string2timestamp(starttime)
    list = []
    while count > 0:
        ts = ts + periodSec
        tp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        if isFutureTradingTime(nowTimeString=tp) is False or isFutureCommonTradingTime(
                security=security,
                nowTimeString=tp) is False:
            continue
        list.append(tp)
        count = count - 1
    return list


# 两个时间差距，返回值单位秒
def diff_time_second(timestr1='2018-01-01 01:55:00', timestr2='2018-01-01 01:54:59'):
    ms_time1 = string2timestamp(timestr1)
    ms_time2 = string2timestamp(timestr2)
    return abs(float(ms_time1) - float(ms_time2))

def string2Datetime(strValue) :
    d = datetime.datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S")
    return d

def now2Datetime():
    now = getYMDHMS()
    d = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    return d

# 时间戳，返回值单位秒
def string2timestamp(strValue):
    try:
        d = datetime.datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S.%f")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        return timeStamp
    except ValueError as e:
        d = datetime.datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        return timeStamp


def getYMDHMS():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getYMD():
    return time.strftime("%Y-%m-%d", time.localtime())


def getHMS():
    return time.strftime("%H:%M:%S", time.localtime())


def getTimeStamp():
    millis = int(round(time.time() * 1000))
    return millis


def getFormatToday():
    return time.strftime("%Y-%m-%d", time.localtime())


def getPreDayYMD(num=1, startdate=None):
    today = datetime.date.today()
    if startdate is not None:
        arr = startdate.split("-")
        today = datetime.date(int(arr[0]), int(arr[1]), int(arr[2]))
    oneday = datetime.timedelta(days=num)
    d = today - oneday
    return str(d)


def get_concept_securities():
    df = ts.get_concept_classified()
    values = df.values
    concept_code_dict = {}
    for row in values:
        code = row[0]
        c_name = row[2]
        if c_name not in concept_code_dict:
            concept_code_dict.setdefault(c_name, [code])
        else:
            concept_code_dict[c_name].append(code)
    return concept_code_dict


def initOpenDateTempFile():
    OpenList = ts.trade_cal()
    rows = OpenList[OpenList.isOpen == 1].values[-888:]
    f = open("../temp_OpenDate.txt", "w")
    f.write("")
    f.close()
    f = open("temp_OpenDate.txt", "a")
    for row in rows:
        date = row[0]
        f.write(date + ";")
    f.close()


def getOpenDates():
    # f = open(os.path.dirname(__file__) + "/temp_OpenDate.txt", "r")
    # str = f.read()
    str = "2017-11-23;2017-11-24;2017-11-27;2017-11-28;2017-11-29;2017-11-30;2017-12-01;2017-12-04;2017-12-05;2017-12-06;2017-12-07;2017-12-08;2017-12-11;2017-12-12;2017-12-13;2017-12-14;2017-12-15;2017-12-18;2017-12-19;2017-12-20;2017-12-21;2017-12-22;2017-12-25;2017-12-26;2017-12-27;2017-12-28;2017-12-29;2018-01-02;2018-01-03;2018-01-04;2018-01-05;2018-01-08;2018-01-09;2018-01-10;2018-01-11;2018-01-12;2018-01-15;2018-01-16;2018-01-17;2018-01-18;2018-01-19;2018-01-22;2018-01-23;2018-01-24;2018-01-25;2018-01-26;2018-01-29;2018-01-30;2018-01-31;2018-02-01;2018-02-02;2018-02-05;2018-02-06;2018-02-07;2018-02-08;2018-02-09;2018-02-12;2018-02-13;2018-02-14;2018-02-22;2018-02-23;2018-02-26;2018-02-27;2018-02-28;2018-03-01;2018-03-02;2018-03-05;2018-03-06;2018-03-07;2018-03-08;2018-03-09;2018-03-12;2018-03-13;2018-03-14;2018-03-15;2018-03-16;2018-03-19;2018-03-20;2018-03-21;2018-03-22;2018-03-23;2018-03-26;2018-03-27;2018-03-28;2018-03-29;2018-03-30;2018-04-02;2018-04-03;2018-04-04;2018-04-09;2018-04-10;2018-04-11;2018-04-12;2018-04-13;2018-04-16;2018-04-17;2018-04-18;2018-04-19;2018-04-20;2018-04-23;2018-04-24;2018-04-25;2018-04-26;2018-04-27;2018-05-02;2018-05-03;2018-05-04;2018-05-07;2018-05-08;2018-05-09;2018-05-10;2018-05-11;2018-05-14;2018-05-15;2018-05-16;2018-05-17;2018-05-18;2018-05-21;2018-05-22;2018-05-23;2018-05-24;2018-05-25;2018-05-28;2018-05-29;2018-05-30;2018-05-31;2018-06-01;2018-06-04;2018-06-05;2018-06-06;2018-06-07;2018-06-08;2018-06-11;2018-06-12;2018-06-13;2018-06-14;2018-06-15;2018-06-19;2018-06-20;2018-06-21;2018-06-22;2018-06-25;2018-06-26;2018-06-27;2018-06-28;2018-06-29;2018-07-02;2018-07-03;2018-07-04;2018-07-05;2018-07-06;2018-07-09;2018-07-10;2018-07-11;2018-07-12;2018-07-13;2018-07-16;2018-07-17;2018-07-18;2018-07-19;2018-07-20;2018-07-23;2018-07-24;2018-07-25;2018-07-26;2018-07-27;2018-07-30;2018-07-31;2018-08-01;2018-08-02;2018-08-03;2018-08-06;2018-08-07;2018-08-08;2018-08-09;2018-08-10;2018-08-13;2018-08-14;2018-08-15;2018-08-16;2018-08-17;2018-08-20;2018-08-21;2018-08-22;2018-08-23;2018-08-24;2018-08-27;2018-08-28;2018-08-29;2018-08-30;2018-08-31;2018-09-03;2018-09-04;2018-09-05;2018-09-06;2018-09-07;2018-09-10;2018-09-11;2018-09-12;2018-09-13;2018-09-14;2018-09-17;2018-09-18;2018-09-19;2018-09-20;2018-09-21;2018-09-25;2018-09-26;2018-09-27;2018-09-28;2018-10-08;2018-10-09;2018-10-10;2018-10-11;2018-10-12;2018-10-15;2018-10-16;2018-10-17;2018-10-18;2018-10-19;2018-10-22;2018-10-23;2018-10-24;2018-10-25;2018-10-26;2018-10-29;2018-10-30;2018-10-31;2018-11-01;2018-11-02;2018-11-05;2018-11-06;2018-11-07;2018-11-08;2018-11-09;2018-11-12;2018-11-13;2018-11-14;2018-11-15;2018-11-16;2018-11-19;2018-11-20;2018-11-21;2018-11-22;2018-11-23;2018-11-26;2018-11-27;2018-11-28;2018-11-29;2018-11-30;2018-12-03;2018-12-04;2018-12-05;2018-12-06;2018-12-07;2018-12-10;2018-12-11;2018-12-12;2018-12-13;2018-12-14;2018-12-17;2018-12-18;2018-12-19;2018-12-20;2018-12-21;2018-12-24;2018-12-25;2018-12-26;2018-12-27;2018-12-28;2018-12-31;2019-01-02;2019-01-03;2019-01-04;2019-01-07;2019-01-08;2019-01-09;2019-01-10;2019-01-11;2019-01-14;2019-01-15;2019-01-16;2019-01-17;2019-01-18;2019-01-21;2019-01-22;2019-01-23;2019-01-24;2019-01-25;2019-01-28;2019-01-29;2019-01-30;2019-01-31;2019-02-01;2019-02-11;2019-02-12;2019-02-13;2019-02-14;2019-02-15;2019-02-18;2019-02-19;2019-02-20;2019-02-21;2019-02-22;2019-02-25;2019-02-26;2019-02-27;2019-02-28;2019-03-01;2019-03-04;2019-03-05;2019-03-06;2019-03-07;2019-03-08;2019-03-11;2019-03-12;2019-03-13;2019-03-14;2019-03-15;2019-03-18;2019-03-19;2019-03-20;2019-03-21;2019-03-22;2019-03-25;2019-03-26;2019-03-27;2019-03-28;2019-03-29;2019-04-01;2019-04-02;2019-04-03;2019-04-04;2019-04-08;2019-04-09;2019-04-10;2019-04-11;2019-04-12;2019-04-15;2019-04-16;2019-04-17;2019-04-18;2019-04-19;2019-04-22;2019-04-23;2019-04-24;2019-04-25;2019-04-26;2019-04-29;2019-04-30;2019-05-02;2019-05-03;2019-05-06;2019-05-07;2019-05-08;2019-05-09;2019-05-10;2019-05-13;2019-05-14;2019-05-15;2019-05-16;2019-05-17;2019-05-20;2019-05-21;2019-05-22;2019-05-23;2019-05-24;2019-05-27;2019-05-28;2019-05-29;2019-05-30;2019-05-31;2019-06-03;2019-06-04;2019-06-05;2019-06-06;2019-06-10;2019-06-11;2019-06-12;2019-06-13;2019-06-14;2019-06-17;2019-06-18;2019-06-19;2019-06-20;2019-06-21;2019-06-24;2019-06-25;2019-06-26;2019-06-27;2019-06-28;2019-07-01;2019-07-02;2019-07-03;2019-07-04;2019-07-05;2019-07-08;2019-07-09;2019-07-10;2019-07-11;2019-07-12;2019-07-15;2019-07-16;2019-07-17;2019-07-18;2019-07-19;2019-07-22;2019-07-23;2019-07-24;2019-07-25;2019-07-26;2019-07-29;2019-07-30;2019-07-31;2019-08-01;2019-08-02;2019-08-05;2019-08-06;2019-08-07;2019-08-08;2019-08-09;2019-08-12;2019-08-13;2019-08-14;2019-08-15;2019-08-16;2019-08-19;2019-08-20;2019-08-21;2019-08-22;2019-08-23;2019-08-26;2019-08-27;2019-08-28;2019-08-29;2019-08-30;2019-09-02;2019-09-03;2019-09-04;2019-09-05;2019-09-06;2019-09-09;2019-09-10;2019-09-11;2019-09-12;2019-09-16;2019-09-17;2019-09-18;2019-09-19;2019-09-20;2019-09-23;2019-09-24;2019-09-25;2019-09-26;2019-09-27;2019-09-30;2019-10-08;2019-10-09;2019-10-10;2019-10-11;2019-10-14;2019-10-15;2019-10-16;2019-10-17;2019-10-18;2019-10-21;2019-10-22;2019-10-23;2019-10-24;2019-10-25;2019-10-28;2019-10-29;2019-10-30;2019-10-31;2019-11-01;2019-11-04;2019-11-05;2019-11-06;2019-11-07;2019-11-08;2019-11-11;2019-11-12;2019-11-13;2019-11-14;2019-11-15;2019-11-18;2019-11-19;2019-11-20;2019-11-21;2019-11-22;2019-11-25;2019-11-26;2019-11-27;2019-11-28;2019-11-29;2019-12-02;2019-12-03;2019-12-04;2019-12-05;2019-12-06;2019-12-09;2019-12-10;2019-12-11;2019-12-12;2019-12-13;2019-12-16;2019-12-17;2019-12-18;2019-12-19;2019-12-20;2019-12-23;2019-12-24;2019-12-25;2019-12-26;2019-12-27;2019-12-30;2019-12-31"
    if str != "":
        dates = str.split(";")
    else:
        return None
    return dates


def get_k_data(df, start, end):
    ret = df[(df['date'] >= start) & (df['date'] <= end)]
    return ret


def isOpen(dateYMD):
    dateYMD = dateYMD[0:10]
    year = dateYMD[0:4]
    if year > '2019':
        print('需要更新OpenDates')
        exit()
    OpenDates = getOpenDates()
    str = ";".join(OpenDates)
    return dateYMD in str


def preOpenDate(date, leftCount=1):
    OpenDates = getOpenDates()
    index = 0
    for d in OpenDates:
        if d == date:
            return OpenDates[index - int(leftCount)]
        index = index + 1
    return None


def getLastestOpenDate(date=getYMD()):
    hms = getHMS()
    if hms >= '15:00:00' and isOpen(date):
        return date
    if hms < '15:00:00' and isOpen(date):
        return preOpenDate(date, 1)
    count = 0
    while True:
        count = count + 1
        if isOpen(date) == False:
            date = getPreDayYMD(1, date)
            continue
        else:
            break
    return date


def nextOpenDate(date, rightCount=1):
    OpenDates = getOpenDates()
    index = 0
    for d in OpenDates:
        if d == date:
            if index + rightCount < OpenDates.__len__() - 1:
                return OpenDates[index + rightCount]
            else:
                break
        index = index + 1
    return None


def getRate(fromPrice, toPrice):
    fromPrice = float(fromPrice)
    toPrice = float(toPrice)
    rate = round(round(((toPrice - fromPrice) / fromPrice), 4) * 100, 4)
    return rate