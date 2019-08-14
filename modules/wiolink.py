import machine

PORT_MAPPING = {
    1: 14,
    2: 12,
    3: 13,
    4: 0,
    5: 3,
    6: 5
}

DEFAULT_PORTS = {
    "LightSensor": 6,
    "TempHumSensor": 3,
    "MoistureSensor": 4,
    "WaterTempSensor": 3,
    "DistanceSensor": 1,
    "MotionSensor": 2,
    "WaterSensorAnalog": 4,
    "WaterSensorDigital": 1,
    "SoundSensor": 4,
    "CO2Sensor": 6,
    "Relay": 1,
    "Servo": 2,
    "LEDStrip": 2,
    "OLEDScreen": 6,
    "LED": 1,
    "Button": 2,
}

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))

class GroveDevice(object):
    
    def __init__(self, port=None):
        if port is None:
            self.port = DEFAULT_PORTS[self.__type__()]
        else:
            self.port = port
        self.pin = machine.Pin(PORT_MAPPING[self.port])

    def __repr__(self):
        return "{0} connected at Port {1}".format(self.__type__(), self.port)

    def __type__(self):
        return type(self).__name__

class GroveI2CDevice(GroveDevice):
    def __init__(self, port=6):
        GroveDevice.__init__(self, port)
        self.check_port(port)
        self.i2c = i2c

    def check_port(self, port):
        if port != 6:
            raise AttributeError("{0} goes only to Port 6.")

class GroveAnalogDevice(GroveDevice):
    def __init__(self, port=4):
        GroveDevice.__init__(self, port)
        self.check_port(port)
        self.pin = machine.ADC(0)

    def check_port(self, port):
        if port != 4:
            raise AttributeError("{0} goes only to Port 4.")