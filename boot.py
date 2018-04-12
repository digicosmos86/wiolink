# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
from machine import Pin
#import webrepl
#webrepl.start()

#import wifimgr
#wlan = wifimgr.get_connection()

p = Pin(13, Pin.OUT)

