from machine import Pin, PWM
from ssd1306 import SSD1306_I2C
from neopixel import NeoPixel
from wiolink import GroveDevice, GroveI2CDevice
import time

tones = {
    'c': 262,
    'd': 294,
    'e': 330,
    'f': 349,
    'g': 392,
    'a': 440,
    'b': 494,
    'C': 523,
    ' ': 0,
}

class Display:
    pass

class Scaler(object):

    def __init__(self, source, target):
        assert len(source)==2, "'source' should be a length 2 tuple or list"
        assert len(target)==2, "'target' should be a length 2 tuple or list"
        self.x1, self.y1 = source
        self.x2, self.y2 = target

    def scale(self, val):
        return self.x2 + (val - self.x1) / (self.y1 - self.x1) * (self.y2 - self.x2)

    def int_scale(self, val):
        return int(self.scale(val))

class ColorScaler(Scaler):

    def __init__(self, source, target):
        Scaler.__init__(self, source, target)
        
    def scale(self, val, x2, y2):
        return x2 + (val - self.x1) / (self.y1 - self.x1) * (y2 - x2)
    
    def int_scale(self, val, x2, y2):
        return int(self.scale(val, x2, y2))

    def scale_color(self, val):
        return [self.int_scale(val, self.x2[i], self.y2[i]) for i in range(3)]


class GroveOutputDevice(GroveDevice):

    def __init__(self, port):
        GroveDevice.__init__(self, port)
        self.check_port(port)

    def check_port(self, port):
        if port == 3:
            raise AttributeError("{0}s cannot be connected to Port 3. Please try Ports 1, 2".format(self.__type__()))
        if port == 4:
            raise AttributeError("Port 4 is an analog port.  Please try Ports 1, 2")
    

class OLEDScreen(GroveI2CDevice, Display, SSD1306_I2C):
    
    def __init__(self, port=None, width=128, height=64, address=0x3c):
        GroveI2CDevice.__init__(self, port)
        if address not in self.i2c.scan():
            raise AttributeError("Please check if the OLED Screen is connected to Port 6 or an I2C hub")
        SSD1306_I2C.__init__(self, width, height, self.i2c, addr=address)
        self.max_line = int(self.height/8)

    def clear(self):
        self.fill(0)

    def _check_max_line(self, line):
        if line > self.max_line:
            raise AttributeError("The {0}x{1} display can only support {2} lines of texts".format(self.width, self.height, self.max_line))

    def clear_line(self, line):
        self._check_max_line(line)
        for y in range(8*(line-1), 8*line):
            for x in range(self.width):
                self.pixel(x, y, 0)

    def write_line(self, line, message):
        if not isinstance(message, str):
            raise TypeError("The message to be shown can only be strings")
        self._check_max_line(line)
        self.text(message, 0, 8*(line-1))

    def show_line(self, line, message):
        self.clear_line(line)
        self.write_line(line, message)
        self.show()

    def show_sensor_data(self, sensor, line):
        reading = sensor.show_data(self, line)
        return reading

class LEDStrip(GroveDevice, NeoPixel):
    def __init__(self, port=None, n=30):
        GroveDevice.__init__(self, port)
        NeoPixel.__init__(self, pin=self.pin, n=n)
        self._on = False
        self._state = 0
        self.input = None
        self.cscaler = None

    def on(self):
        blue_modulo = 3
        for i in range(self.n):
            NeoPixel.__setitem__(self, i, (255, 0, 0))
            if i % blue_modulo == 0:
                NeoPixel.__setitem__(self, i, (61, 0, 255))
        NeoPixel.write(self)
        self._on=True

    def off(self):
        NeoPixel.fill(self, (0, 0, 0))
        NeoPixel.write(self)
        self._on=False

    def is_on(self):
        on = self._on
        return on

    def set_state(self, state):
        self._state = state

    def get_state(self):
        return self._state

    def blink(self, color=[255, 255, 255], times=3, interval=0.5):
        try:
            self.off()
            for _ in range(times):
                NeoPixel.fill(self, color)
                NeoPixel.write(self)
                time.sleep(interval)
                NeoPixel.fill(self, [0, 0, 0])
                NeoPixel.write(self)
                time.sleep(interval)
        finally:
            self.off()

    def update(self):
        self.write()

    def cycle(self, interval_ms=25, color=(255, 255, 255), times=4):
        try:
            self.off()
            for i in range(times * self.n):
                for j in range(self.n):
                    NeoPixel.__setitem__(self, j, (0, 0, 0))
                NeoPixel.__setitem__(self, i % self.n, color)
                NeoPixel.write(self)
                time.sleep_ms(interval_ms)
        finally:
            self.off()

    def bounce(self, interval_ms=60, color=(0, 0, 128), times=4):
        try:
            self.off()
            for i in range(times * self.n):
                for j in range(self.n):
                    NeoPixel.__setitem__(self, j, color)
                if (i // self.n) % 2 == 0:
                    NeoPixel.__setitem__(self, i % self.n, (0, 0, 0))
                else:
                    NeoPixel.__setitem__(self, self.n - 1 - (i % self.n), (0, 0, 0))
                NeoPixel.write(self)
                time.sleep_ms(interval_ms)
        finally:
            self.off()

    def fade(self, times=4):
        try:
            self.off()
            for i in range(0, times * 256, 8):
                for j in range(self.n):
                    if (i // 256) % 2 == 0:
                        val = i & 0xff
                    else:
                        val = 255 - (i & 0xff)
                    NeoPixel.__setitem__(self, j, [val, 0, 128])
                NeoPixel.write(self)
        finally:
            self.off()

    def demo(self, program="cycle"):
        self.off()
        try:
            self.cycle()
            self.bounce()
            self.fade()
        finally:
            self.off()

    def set_input(self, input, low=0, high=500, color_x=(0, 0, 0), color_y=(255, 255, 255)):
        self.input = input
        self.cscaler = ColorScaler([low, high], [color_x, color_y])

    def refresh(self):
        if not input:
            raise ValueError("Please specify an input sensor")

        self.fill(self.cscaler.scale_color(self.input.get_data()))
        self.write()
        


class LED(GroveOutputDevice):
    def __init__(self, port=None):
        GroveOutputDevice.__init__(self, port)
        if self._on:
            self.led = PWM(self.pin, freq=50, duty=1023)
        else:
            self.led = PWM(self.pin, freq=50, duty=0)
        self._on = False
    
    def on(self, fade=False, duration=1):
        if self._on:
            return
        if fade:
            for i in range(50):
                self.led.duty(int(1023*((i+1)/50)))
                time.sleep_ms(int(duration*1000/50))
        else:
            self.led.duty(1023)
        self._on=True
    
    def off(self, fade=False, duration=1):
        if not self._on:
            return
        if fade:
            for i in range(50):
                self.led.duty(1023-int(1023*((i+1)/50)))
                time.sleep_ms(int(duration*1000/50))
        else:
            self.led.duty(0)
        self._on=False

    def is_on(self):
        return self._on

class Servo(GroveOutputDevice):

    def __init__(self, port=None, position=0):
        GroveOutputDevice.__init__(self, port)
        self.scaler = Scaler((0, 180), (35, 132))
        self.servo = PWM(self.pin, duty=self._degree2duty(position), freq=50)
        self.position = position

    def set_position(self, degree):
        self.servo.duty(self._degree2duty(degree))
        self.position = degree

    def get_position(self):
        return self.position

    def _degree2duty(self, degree):
        if degree < 0 or degree > 180:
            raise ValueError("Please choose a degree between 0 and 180")
        return self.scaler.int_scale(degree)


class Relay(GroveOutputDevice):
    def __init__(self, port=None):
        GroveOutputDevice.__init__(self, port)
        self.pin.init(mode = Pin.OUT)
        
    def on(self):
        self.pin.value(1)

    def off(self):
        self.pin.vaule(0)

    def get_status(self):
        return self.pin.value()


class Buzzer(GroveOutputDevice):
    def __init__(self, port=None):
        GroveOutputDevice.__init__(self, port)
        self.buzzer = PWM(self.pin)

    def play_note(self, note, duration=0.5):
        if len(note) != 1:
            raise ValueError("This method only plays one note!")
        if note not in tones:
            raise ValueError("Note not supported!")
        try:
            self.buzzer.freq(tones[note])
            self.buzzer.duty(256)
            time.sleep(duration)
        finally:
            self.buzzer.deinit()

    def play_music(self, notes, rhythms=None, tempo=1):
        if rhythms is None:
            rhythms = [1]*len(notes)
        if len(notes) != len(rhythms):
            raise ValueError("Rhythms must have same length as notes!")
        if any(x <= 0 for x in rhythms):
            raise ValueError("Rhythms cannot have zero or negative values!")
        if any(note not in tones for note in notes):
            raise ValueError("Some notes are not supported!")
        try:
            for note, rhythm in zip(notes, rhythms):
                self.buzzer.freq(tones[note])
                self.buzzer.duty(256)
                time.sleep(tempo/rhythm)
        finally:
            self.buzzer.deinit()