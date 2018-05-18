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
    "TemperatureSensor": 3,
    "TemperatureSensorPro": 3,
    "MoistureSensor": 4,
    "Relay": 1,
    "Servo": 2,
    "GrowLight": 2,
    "OledScreen": 6,
    "Led": 1,
    "Button": 2,
    "Buzzer": 2
}

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))

class GroveDevice:
    
    def __init__(self, type, port):
        self.check_port(type, port)
        self.type = type
        self.port = port

    def check_port(self, type, port):
        if type == "MoistureSensor" and port != 4:
            raise OSError("The moisture sensor is an analog sensor. You can only connect it to Port 4.")
        if type == "LightSensor" and port != 6:
            raise OSError("The light sensor is an i2c device. You can only connect it to Port 6 or the I2C hub.")
        if type == "OledScreen" and port != 6:
            raise OSError("The OLED screen is an i2c device. You can only connect it to Port 6 or the I2C hub.")
        if port == 5:
            print("Warning: using Port 5 while programming might cause unexpected problems. Please consider switching the device to other ports.")

    def __repr__(self):
        return "{0} connected at Port {1}".format(self.type, self.port)