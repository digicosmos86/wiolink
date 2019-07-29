# This file is executed on every boot (including wake-boot from deepsleep)

# Disable OS Debugging Messages
import esp
esp.osdebug(None)

# Set GPIO13 to HIGH to enable current to Grove device
from machine import Pin
import sys

Pin(13, Pin.OUT)

# Perform garbage collection
import gc
gc.collect()