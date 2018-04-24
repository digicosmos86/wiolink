# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
from machine import Pin
import sys
#import webrepl
#webrepl.start()

#import wifimgr
#wlan = wifimgr.get_connection()

Pin(13, Pin.OUT)
p = Pin(0, Pin.IN, Pin.PULL_UP)
if p.value() == 1:
    sys.exit()
gc.collect()