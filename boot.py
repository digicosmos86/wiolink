# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import machine
#import webrepl
#webrepl.start()

#import wifimgr
#wlan = wifimgr.get_connection()

machine.Pin(13, Pin.OUT)
gc.collect()