from traderbody import TraderBody
import time
import util.tools as util

ft = 5
tt = 10
rt = 65
rb = 35
rtp = 9
trader = TraderBody(security='RB8888.XSGE', frequency='17m',
                    layer1_from_timeperiod=ft,
                    layer1_to_timeperiod=tt,
                    layer1_rsi_top=rt,
                    layer1_rsi_bottom=rb,
                    layer1_rsi_timeperiod=rtp
                    )
while True:
    trader.tick()
    time.sleep(6)
    print('[' + util.getYMDHMS() + ']: tick...')
