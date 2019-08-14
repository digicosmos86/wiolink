from machine import Pin
from wiolink import GroveDevice, GroveI2CDevice, GroveAnalogDevice
from utime import ticks_ms, ticks_us
from time import sleep, sleep_ms, sleep_us
import ustruct

CMD_START = b"\x00\x10"
CMD_STOP = b"\x01\x04"
CMD_INTERVAL = b"\x46\x00"
CMD_READY = b"\x02\x02"
CMD_READ = b"\x03\x00"
CMD_ASC = b"\x53\x06"
CMD_FRC = b"\x52\x04"
CMD_TEMP_OFFSET = b"\x54\x03"
CMD_ALTITUDE = b"\x51\x02"
CMD_FIRMWARE = b"\xD1\x00"
CMD_RESET = b"\xD3\x04"

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


class TempHumSensor(GroveDevice, Displayable):
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


class CO2Sensor(GroveI2CDevice):

    def __init__(self, port=6, address=0x61):
        GroveI2CDevice.__init__(self, port=6)
        self.address = address
        if self.address not in self.i2c.scan():
            raise OSError("Please check if the CO2 sensor is connected to Port 6 or an I2C hub")
        self.measures = None
        self._write(CMD_START + b"\x00\x00\x81")
        sleep(0.5)

    def _read(self, location, length):
        self.i2c.writeto(self.address, location)
        return self.i2c.readfrom(self.address, length)

    def _write(self, command, data=None):
        if data:
            pass

        self.i2c.writeto(self.address, command)

    def _crc8(self, data):
        crc = 0xFF

        for elem in data:
            crc ^= elem

            for shift in range(8):
                if (crc & 0x80):
                    crc = ((crc << 1) ^ 0x31) % 0x100
                else:
                    crc = crc << 1

        return crc

    def check_crc(self, data):
        for offset in range(0, len(data), 3):
            if not data[offset+2] == self._crc8(data[offset:offset+2]):
                print(offset, data[offset:offset+3])
                return False
        return True

    def read(self):

        data_raw = self._read(CMD_READ, 18)
        data_crc = self.check_crc(data_raw)
        if not data_crc:
            return False

        co2 = ustruct.unpack(">f", data_raw[0:2] + data_raw[3:5])[0]
        temp = ustruct.unpack(">f", data_raw[6:8] + data_raw[9:11])[0]
        hum = ustruct.unpack(">f", data_raw[12:14] + data_raw[15:17])[0]

        return co2, temp, hum

    def get_temp(self, celsius=False):
        self.__check_refresh()
        if celsius:
            return self.measures[1]
        return self.measures[1] * 1.8 + 32

    def get_humidity(self):
        self.__check_refresh()
        return self.measures[2]

    def get_CO2(self):
        self.__check_refresh()
        return self.measures[0]

    def get_status_ready(self):
        ready_raw = self._read(CMD_READY, 3)
        ready_crc = self.check_crc(ready_raw)
        ready = ustruct.unpack(">H", ready_raw[0:2])[0]
        return ready and ready_crc

    def set_measurement_interval(self, interval):
        bint = ustruct.pack('>H', interval)
        crc = self._crc8(bint)
        data = bint + bytes([crc])
        self.i2c.writeto_mem(self.address, 0x4600, data, addrsize=16)

    def get_measurement_interval(self):
        bint = self.i2c.readfrom_mem(self.address, 0x4600, 3, addrsize=16)
        self.check_crc(bint)
        return ustruct.unpack('>H', bint)[0]

    def __check_refresh(self):
        if self.get_status_ready():
            self.measures = self.read()
        else:
            if self.measures is None:
                print("Sensor initializing. Please wait.")
                while not self.get_status_ready():
                    sleep(1)
                self.measures = self.read()

    def get_data(self):
        self.__check_refresh()
        return self.measures

    def send_data(self, screen, line, line2=None, text1=None, text2=None):
        Displayable.check_display(screen)
        reading = self.get_data()
        if text1 is None:
            msg1 = ">{0}: {1:.2f} ppm".format(self.port, reading[0])
        else:
            msg1 = "{0}: {1:.2f} ppm".format(text1, reading[0])
        if text2 is None:
            msg2 = ">{0}: {1:.1f}F {2:.1f}%".format(self.port, reading[1], reading[2])
        else:
            msg2 = "{0}: {1:.1f}F {2:.1f}%".format(text2, reading[1], reading[2])
        screen.show_line(line, msg1)
        if line2 is None:
            screen.show_line(line+1, msg2)
        else:
            screen.show_line(line2, msg2)
        return reading