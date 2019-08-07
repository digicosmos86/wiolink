from machine import Pin, PWM
from ssd1306 import SSD1306_I2C
from neopixel import NeoPixel
from wio_link import PORT_MAPPING, DEFAULT_PORTS, GroveDevice, i2c
import time

class Display(GroveDevice):

    def __init__(self, type, port):
        GroveDevice.__init__(self, type, port)


class OledScreen(Display, SSD1306_I2C):
    
    def __init__(self, port=DEFAULT_PORTS["OledScreen"], width=128, height=64, address=0x3c):
        if address not in i2c.scan():
            raise OSError("Please check if the OLED Screen is connected to Port 6 or an I2C hub")
        Display.__init__(self, "OledScreen", port)
        SSD1306_I2C.__init__(self, width, height, i2c, addr=address)
        self.max_line = int(self.height/8)

    def clear(self):
        self.fill(0)

    def _check_max_line(self, line):
        if line > self.max_line:
            raise ValueError("The {0}x{1} display can only support {2} lines of texts".format(self.width, self.height, self.max_line))

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

class GrowLight(Display, NeoPixel):
    def __init__(self, port=DEFAULT_PORTS["GrowLight"], n=30):
        Display.__init__(self, "GrowLight", port)
        NeoPixel.__init__(self, pin=Pin(PORT_MAPPING[port]), n=n)
        self._on=False

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

    def blink(self, color=[255, 255, 255], times=3, interval=0.5):
        try:
            self.off()
            for i in range(times):
                NeoPixel.fill(self, color)
                NeoPixel.write(self)
                time.sleep(interval)
                NeoPixel.fill(self, [0, 0, 0])
                NeoPixel.write(self)
                time.sleep(interval)
        finally:
            self.off()

    def demo(self, program="cycle"):
        self.off()

        try:
            n = self.n

            if program == "cycle":
                for i in range(4 * n):
                    for j in range(n):
                        NeoPixel.__setitem__(self, j, [0, 0, 0])
                    NeoPixel.__setitem__(self, i % n, [255, 255, 255])
                    NeoPixel.write(self)
                    time.sleep_ms(25)
            elif program == "bounce":
                for i in range(4 * n):
                    for j in range(n):
                        NeoPixel.__setitem__(self, j, [0, 0, 128])
                    if (i // n) % 2 == 0:
                        NeoPixel.__setitem__(self, i % n, [0, 0, 0])
                    else:
                        NeoPixel.__setitem__(self, n - 1 - (i % n), [0, 0, 0])
                    NeoPixel.write(self)
                    time.sleep_ms(60)
            elif program == "fade":
                for i in range(0, 4 * 256, 8):
                    for j in range(n):
                        if (i // 256) % 2 == 0:
                            val = i & 0xff
                        else:
                            val = 255 - (i & 0xff)
                        NeoPixel.__setitem__(self, j, [val, 0, 128])
                    NeoPixel.write(self)
        finally:
            self.off()


class Led(Display):
    def __init__(self, port=DEFAULT_PORTS["Led"]):
        Display.__init__(self, "Led", port)
        self.led = PWM(Pin(PORT_MAPPING[port]), freq=50, duty=0)
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
        on = self._on
        return on