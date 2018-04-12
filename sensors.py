from machine import I2C, Pin, ADC
from dht import DHT11, DHT22
from wio_link import PORT_MAPPING

from tsl2561 import TSL2561

from utime import ticks_ms

i2c = I2C(scl=Pin(5), sda=Pin(4))


class LightSensor(TSL2561):
    def __init__(self, port = 6, address = 0x29):
        if port != 6:
            raise OSError("Light sensors have to be connected to Port 6")
        if address not in i2c.scan():
            raise OSError("Please check if the light sensor is connected to Port 6 or an I2C hub")

        TSL2561.__init__(self, i2c, address = address)

    def get_lux(self):
        return TSL2561.read(self)


class TemperatureSensor(DHT11):
    def __init__(self, port=3):
        if port == 4:
            raise OSError("Port 4 is an analog port. Please try other ports")
        if port == 6:
            print("Port 6 is usually reserved for OLED screens and light sensors. Please consider other ports (Port 3 recommended).")
        self.port = port
        self.last_measure = 0
        DHT11.__init__(self, Pin(PORT_MAPPING[port]))

    def get_temperature(self, celsius=FALSE):
        now = ticks_ms()
        if self.last_measure == 0 or now - self.last_measure > 1000:
            try:
                DHT11.measure(self)
            except OSError:
                raise OSError("Please check if sensor is connected to Port {0}".format(self.port))
        self.last_measure = now
        if celsius:
            return DHT11.temperature(self)
        return DHT11.temperature(self) * 1.8 + 32
        
    def get_humidity(self):
        now = ticks_ms()
        if self.last_measure == 0 or now - self.last_measure > 1000:
            try:
                DHT11.measure(self)
            except OSError:
                raise OSError("Please check if sensor is connected to Port {0}".format(self.port))
        self.last_measure = now
        return DHT11.humidity(self)


class TemperatureSensorPro(DHT22):
    def __init__(self, port=3):
        if port == 4:
            raise ValueError("Port 4 is an analog port. Please try other ports")
        if port == 6:
            print("Port 6 is usually reserved for OLED screens and light sensors. Please consider other ports (Port 3 recommended).")
        self.port = port
        self.last_measure = 0
        DHT22.__init__(self, Pin(PORT_MAPPING[port]))

    def get_temperature(self, celsius=FALSE):
        now = ticks_ms()
        if self.last_measure == 0 or now - self.last_measure > 500:
            try:
                DHT22.measure(self)
            except OSError:
                raise OSError("Please check if sensor is connected to Port {0}".format(self.port))
        self.last_measure = now
        if celsius:
            return DHT22.temperature(self)
        return DHT22.temperature(self) * 1.8 + 32
        
    def get_humidity(self):
        now = ticks_ms()
        if self.last_measure == 0 or now - self.last_measure > 500:
            try:
                DHT22.measure(self)
            except OSError:
                raise OSError("Please check if sensor is connected to Port {0}".format(self.port))
        self.last_measure = now
        return DHT22.humidity(self)

class MoistureSensor(ADC):
    def __init__(self, port = 4):
        if port != 4:
            raise OSError("Moisture sensors can only be connected to Port 4!")
        ADC.__init__(self, 0)

    def get_moisture(self):
        return ADC.read(self)

