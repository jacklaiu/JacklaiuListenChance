from traderbody import TraderBody
import time
import util.tools as util

ft = 6
tt = 23
rt = 50
rb = 50
rtp = 9
layer2_stoprate = 0.01
layer2_fromstartrate = 0.99
layer2_getLastestPrice_frequency = '5m'
trader = TraderBody(security='RB8888.XSGE', frequency='58m',
                    layer1_from_timeperiod=ft,
                    layer1_to_timeperiod=tt,
                    layer1_rsi_top=rt,
                    layer1_rsi_bottom=rb,
                    layer1_rsi_timeperiod=rtp,
                    layer2_stoprate=layer2_stoprate,
                    layer2_fromstartrate=layer2_fromstartrate,
                    layer2_getLastestPrice_frequency=layer2_getLastestPrice_frequency)
while True:
    print('[' + util.getYMDHMS() + ']: tick...')
    trader.tick()
    time.sleep(50)





# ft = 6
# tt = 23
# rt = 50
# rb = 50
# rtp = 9
# layer2_stoprate = 0.01
# layer2_fromstartrate = 0.99
# layer2_getLastestPrice_frequency = '5m'
# trader = TraderBody(security='RB8888.XSGE', frequency='58m',
#                     starttime_fortest='2019-01-12 09:00:00',
#                     endtime_fortest='2019-06-13 22:00:00',
#                     layer1_from_timeperiod=ft,
#                     layer1_to_timeperiod=tt,
#                     layer1_rsi_top=rt,
#                     layer1_rsi_bottom=rb,
#                     layer1_rsi_timeperiod=rtp,
#                     layer2_stoprate=layer2_stoprate,
#                     layer2_fromstartrate=layer2_fromstartrate,
#                     layer2_getLastestPrice_frequency=layer2_getLastestPrice_frequency)
#
# trader.testMain()
# total_rate = 1
# for r in trader.rates_markAtHandleAction:
#     total_rate = total_rate * r
# print(total_rate)
# print(ft)
# print(tt)
# print(rt)
# print(rb)
# print(layer2_stoprate)
# print(layer2_fromstartrate)
# print("trader.rates_markAtHandleAction: " + str(sorted(trader.rates_markAtHandleAction)))