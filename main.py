## import libraries

from sensors import TemperatureSensorPro, LightSensor
from actuators import Relay, Servo
from displays import OledScreen, GrowLight
import time

micropython.mem_info(1)

## set environment variables

SAMPLE_RATE = 10 # Sends data every 10 seconds
TEMP_THRESHOLD = 77
LUX_THRESHOLD = 100

## register devices

relay = Relay(1)
servo = Servo(2, position=175)
temp_sensor = TemperatureSensorPro(3)
gl = GrowLight(5)
light_sensor = LightSensor(6)
screen = OledScreen(6)

## main loop

while True:
    t = temp_sensor.get_temperature()
    h = temp_sensor.get_humidity()
    l = light_sensor.get_lux()

    temp_sensor.show_data(screen, 1)
    light_sensor.show_data(screen, 2)

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