from machine import Pin, ADC
from dht import DHT11, DHT22
from wio_link import PORT_MAPPING, DEFAULT_PORTS, GroveDevice, i2c
from displays import Display

from tsl2561 import TSL2561

from utime import ticks_ms

class Sensor(GroveDevice):
    def __init__(self, type, port):
        GroveDevice.__init__(self, type, port)
    
    def get_data(self):
        pass

    def show_data(self, screen, line):
        pass


class LightSensor(Sensor, TSL2561):
    def __init__(self, port=DEFAULT_PORTS["LightSensor"], address=0x29):
        Sensor.__init__(self, "LightSensor", port)
        if address not in i2c.scan():
            raise OSError("Please check if the light sensor is connected to Port 6 or an I2C hub")

        TSL2561.__init__(self, i2c, address = address)

    def get_lux(self):
        return TSL2561.read(self)

    def get_data(self):
        return TSL2561.read(self)

    def show_data(self, screen, line):
        if not isinstance(screen, Display):
            raise TypeError("The 'screen' parameter must be an instance of Display!")
        reading = TSL2561.read(self)
        msg = ">{0}: {1} lux".format(self.port, reading)
        screen.show_line(line, msg)
        return reading


class TemperatureSensor(Sensor, DHT11):
    def __init__(self, port=DEFAULT_PORTS["TemperatureSensor"]):
        Sensor.__init__(self, "TemperatureSensor", port)
        DHT11.__init__(self, Pin(PORT_MAPPING[port]))
        self.last_measure = 0

    def _check_refresh(self, min_refresh_rate):
        now = ticks_ms()
        if self.last_measure == 0 or now - self.last_measure > min_refresh_rate:
            try:
                DHT11.measure(self)
            except OSError:
                raise OSError("Please check if sensor is connected to Port {0}".format(self.port))
        self.last_measure = now

    def get_temperature(self, celsius=False):
        self._check_refresh(1000)
        if celsius:
            return DHT11.temperature(self)
        return DHT11.temperature(self) * 1.8 + 32
        
    def get_humidity(self):
        self._check_refresh(1000)
        return DHT11.humidity(self)

    def get_data(self):
        self._check_refresh(1000)
        return (DHT11.temperature(self) * 1.8 + 32, DHT11.humidity(self))

    def show_data(self, screen, line):
        if not isinstance(screen, Display):
            raise TypeError("The 'screen' parameter must be an instance of Display!")
        reading = self.get_data()
        msg = ">{0}: {1}F {2}%".format(self.port, reading[0], reading[1])
        screen.show_line(line, msg)
        return reading


class TemperatureSensorPro(Sensor, DHT22):
    def __init__(self, port=DEFAULT_PORTS["TemperatureSensor"]):
        Sensor.__init__(self, "TemperatureSensorPro", port)
        DHT22.__init__(self, Pin(PORT_MAPPING[port]))
        self.last_measure = 0

    def _check_refresh(self, min_refresh_rate):
        now = ticks_ms()
        if self.last_measure == 0 or now - self.last_measure > min_refresh_rate:
            try:
                DHT22.measure(self)
            except OSError:
                raise OSError("Please check if sensor is connected to Port {0}".format(self.port))
        self.last_measure = now

    def get_temperature(self, celsius=False):
        self._check_refresh(500)
        if celsius:
            return DHT22.temperature(self)
        return DHT22.temperature(self) * 1.8 + 32
        
    def get_humidity(self):
        self._check_refresh(500)
        return DHT22.humidity(self)

    def get_data(self):
        self._check_refresh(500)
        return (DHT22.temperature(self) * 1.8 + 32, DHT22.humidity(self))

    def show_data(self, screen, line):
        if not isinstance(screen, Display):
            raise TypeError("The 'screen' parameter must be an instance of Display!")
        reading = self.get_data()
        msg = ">{0}: {1}F {2}%".format(self.port, reading[0], reading[1])
        screen.show_line(line, msg)
        return reading


class MoistureSensor(Sensor):
    def __init__(self, port=DEFAULT_PORTS["MoistureSensor"]):
        Sensor.__init__(self, "MoistureSensor", port)
        self.pin = ADC(0)

    def get_moisture(self):
        return self.pin.read()

    def get_data(self):
        return self.pin.read(self)

    def show_data(self, screen, line):
        if not isinstance(screen, Display):
            raise TypeError("The 'screen' parameter must be an instance of Display!")
        reading = self.pin.read()
        msg = ">{0}: {1}".format(self.port, reading)
        screen.show_line(line, msg)
        return reading
