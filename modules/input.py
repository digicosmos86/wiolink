from machine import Pin
from wiolink import GroveDevice, GroveI2CDevice, GroveAnalogDevice
from utime import ticks_ms, ticks_us
from time import sleep_ms, sleep_us

class Displayable:

    @staticmethod
    def check_display(screen):
        from output import Display
        if not isinstance(screen, Display):
            raise TypeError("Please check the first argument. Can it display stuff?")


class LightSensor(GroveI2CDevice, Displayable):
    def __init__(self, port=6, address=0x29):
        GroveI2CDevice.__init__(self)
        if address not in self.i2c.scan():
            raise OSError("Please check if the light sensor is connected to Port 6 or an I2C hub")
        from tsl2561 import TSL2561
        self.ls = TSL2561(self.i2c, address = address)

    def get_lux(self):
        return self.ls.read(self)

    def get_data(self):
        return self.ls.read(self)

    def show_data(self, screen, line, text=None):
        Displayable.check_display(screen)
        reading = self.ls.read(self)
        if text is None:
            msg = ">{0}: {1} lux".format(self.port, reading)
        else:
            msg = "{0}: {1} lux".format(text, reading)
        screen.show_line(line, msg)
        return reading


class TempSensor(GroveDevice, Displayable):
    def __init__(self, port=None, pro = True):
        GroveDevice.__init__(self, port)
        if pro:
            from dht import DHT22
            self.dht = DHT22(self.pin)
            self._DEFAULT_REFRESH = 500
        else:
            from dht import DHT11
            self.dht = DHT11(self.pin)
            self._DEFAULT_REFRESH = 1000
        self.last_measure = 0

    def _check_refresh(self, min_refresh_rate):
        now = ticks_ms()
        if self.last_measure == 0 or now - self.last_measure > min_refresh_rate:
            try:
                self.dht.measure()
            except OSError:
                raise OSError("Please check if sensor is connected to Port {0}".format(self.port))
        self.last_measure = now

    def get_temp(self, celsius=False):
        self._check_refresh(self._DEFAULT_REFRESH)
        if celsius:
            return self.dht.temperature()
        return self.dht.temperature() * 1.8 + 32
        
    def get_humidity(self):
        self._check_refresh(self._DEFAULT_REFRESH)
        return self.dht.humidity()

    def get_data(self):
        self._check_refresh(self._DEFAULT_REFRESH)
        return (self.dht.temperature() * 1.8 + 32, self.dht.humidity())

    def send_data(self, screen, line, text=None):
        Displayable.check_display(screen)
        reading = self.get_data()
        if text is None:
            msg = ">{0}: {1}F {2}%".format(self.port, reading[0], reading[1])
        else:
            msg = "{0}: {1}F {2}%".format(text, reading[0], reading[1])
        screen.show_line(line, msg)
        return reading


class MoistureSensor(GroveAnalogDevice, Displayable):
    def __init__(self, port=4):
        GroveAnalogDevice.__init__(self, port)

    def get_moisture(self):
        return self.pin.read()

    def get_data(self):
        return self.pin.read()

    def show_data(self, screen, line, text=None):
        self.check_display(screen)
        reading = self.pin.read()
        if text is None:
            msg = ">{0}: {1}".format(self.port, reading)
        else:
            msg = "{0}: {1}".format(text, reading)
        screen.show_line(line, msg)
        return reading


class WaterTempSensor(GroveDevice, Displayable):
    def __init__(self, port=None):
        GroveDevice.__init__(self, port)

        from onewire import OneWire
        from ds18x20 import DS18X20

        self.ds = DS18X20(OneWire(self.pin))

        addrs = self.ds.scan()
        if not addrs:
            raise OSError("Please check if sensor is connected to Port {0}".format(self.port))

        self.addr = addrs.pop()

    def get_temp(self, celsius=False):
        self.ds.convert_temp()
        sleep_ms(750)
        temp = self.ds.read_temp(self.addr)
        if celsius:
            return temp
        else:
            return temp * 1.8 + 32

    def get_data(self):
        return self.get_temp()

    def show_data(self, screen, line, text=None):
        Displayable.check_display(screen)
        reading = self.get_data()
        if text is None:
            msg = ">{0}: {1:.2f}F%".format(self.port, reading)
        else:
            msg = "{0}: {1} lux".format(text, reading)
        screen.show_line(line, msg)
        return reading


class DistanceSensor(GroveDevice):
    
    def __init__(self, port=None, timeout=500*2*30):
        GroveDevice.__init__(self, port)
        self.timeout = timeout
        self.pin.init(mode=Pin.OUT, pull=None)
        self.pin.value(0)

    def _micros_diff(self, begin, end):
        return end - begin

    def _pulse_in(self):
        begin = ticks_us()

        while self.pin.value() == 1:
            if self._micros_diff(begin, ticks_us()) >= self.timeout:
                return 0

        while self.pin.value() != 1:
            if self._micros_diff(begin, ticks_us()) >= self.timeout:
                return 0
            pulse_begin = ticks_us()

        while self.pin.value() == 1:
            if self._micros_diff(begin, ticks_us()) >= self.timeout:
                return 0
            pulse_end = ticks_us()

        return self._micros_diff(pulse_begin, pulse_end)


    def _measure(self):

        self.pin.init(mode=Pin.OUT)
        self.pin.value(0)
        sleep_us(2)
        self.pin.value(1)
        sleep_us(5)
        self.pin.value(0)
        self.pin.init(mode=Pin.IN)
        return self._pulse_in()

    def get_distance(self, digits=2, cm=False):

        pulse_time = self._measure()

        if pulse_time == 0:
            return 0

        if cm:
            result = pulse_time/2/29.1
        else:
            result = pulse_time/2/73.746

        return round(result, digits)


class Button(GroveDevice):
    def __init__(self, port=None):
        GroveDevice.__init__(self, port)
        self.pin.init(Pin.IN, Pin.PULL_UP)

    def is_pressed(self):
        return True if self.pin.value() == 1 else False

    def on_press(self, callback):
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=callback)

    def on_release(self, callback):
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)


class MotionSensor(GroveDevice):

    def __init__(self, port=None):
        GroveDevice.__init__(self, port)
        self.pin.init(mode=Pin.IN, pull=None)

    def is_activated(self):
        return True if self.pin.value() == 1 else False

    def on_detect(self, callback):
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=callback)

    def on_reset(self, callback):
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)


class WaterSensorDigital(GroveDevice):
    def __init__(self, port=None):
        GroveDevice.__init__(self, port)
        self.pin.init(mode=Pin.IN, pull=None)

    def is_wet(self):
        return True if self.pin.value() == 0 else False

    def is_dry(self):
        return True if self.pin.value() == 1 else False

    def on_dry(self, callback):
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=callback)

    def on_wet(self, callback):
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)


class WaterSensorAnalog(GroveAnalogDevice, Displayable):
    def __init__(self, port=4):
        GroveAnalogDevice.__init__(self, port)

    def get_moisture(self):
        return self.pin.read()

    def get_data(self):
        return self.pin.read()

    def show_data(self, screen, line, text=None):
        self.check_display(screen)
        reading = self.pin.read()
        if text is None:
            msg = ">{0}: {1}".format(self.port, reading)
        else:
            msg = "{0}: {1}".format(text, reading)
        screen.show_line(line, msg)
        return reading


def WaterSensor(port=None):
    if port == 4:
        return WaterSensorAnalog()
    else:
        return WaterSensorDigital(port)


class SoundSensor(GroveAnalogDevice):
    def __init__(self, port=4):
        GroveAnalogDevice.__init__(self, port)

    def get_sound_level(self):
        return self.pin.read()

    def get_data(self):
        return self.pin.read()