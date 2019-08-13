## import libraries

from input import TempHumSensor, LightSensor
from output import Relay, Servo, OLEDScreen, LEDStrip
import time

print("Starting...")
time.sleep(5)

## set environment variables

SAMPLE_RATE = 10 # Sends data every 10 seconds
TEMP_THRESHOLD = 77
LUX_THRESHOLD = 100

## register devices

relay = Relay(1)
servo = Servo(2, position=175)
temp_sensor = TempHumSensor(3)
gl = LEDStrip(5)
light_sensor = LightSensor(6)
screen = OLEDScreen(6)

## main loop

while True:

    t, h = temp_sensor.show_data(screen, 1)
    l = light_sensor.show_data(screen, 2)

    if t > TEMP_THRESHOLD:
        relay.on()
        servo.set_position(95)
    else:
        relay.off()
        servo.set_position(175)

    if l < LUX_THRESHOLD:
        gl.on()
    else:
        gl.off()

    time.sleep(SAMPLE_RATE)