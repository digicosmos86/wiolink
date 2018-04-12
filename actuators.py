from machine import Pin, PWM
from neopixel import NeoPixel
from wio_link import PORT_MAPPING


def degree2duty(degree, start=35, end=132):  # Hobby servo motors can be controlled using PWM. They require a\
    # frequency of 50Hz and then a duty between about 33 and 141, with 77 being the centre value

    if degree < 0 or degree > 180:
        raise ValueError("Please choose a degree between 0 and 180")
    return int(start + (end - start) * (degree / 180))


class Servo:

    def __init__(self, port=2, position=0):
        if port == 3:
            raise OSError("Servos cannot be connected to Port 3. Please try Ports 1, 2, or 5")
        elif port == 4:
            raise OSError("Port 4 is an analog port.  Please try Ports 1, 2, or 5.")
        elif port == 6:
            print("Port 6 is usually reserved for OLED screens and light sensors. \
                  Please consider other ports (Port 2 recommended).")
        self.servo = PWM(Pin(PORT_MAPPING[port]), duty=degree2duty(init_degree), freq=50)
        self.position = position

    def set_position(self, degree):
        self.servo.duty(degree2duty(degree))
        self.position = degree

    def get_position(self):
        return self.position


class Relay:

    def __init__(self, port = 1):
        if port == 3:
            raise OSError("Relays cannot be connected to Port 3. Please try Ports 1, 2, or 5")
        elif port == 4:
            raise OSError("Port 4 is an analog port.  Please try Ports 1, 2, or 5.")
        elif port == 6:
            print("Port 6 is usually reserved for OLED screens and light sensors. Please consider other ports \
                  Port 1 is recommended).")
        self.relay = Pin(PORT_MAPPING[port], Pin.OUT)
        
    def on(self):
        self.relay.on()

    def off(self):
        self.relay.off()

    def status(self):
        return self.relay.value()


class GrowLight(NeoPixel):
    def __init__(self, port = 5, n = 60):
        if port == 4:
            raise OSError("Port 4 is an analog port.  Please try Ports 1, 2, 3 or 5.")
        elif port == 6:
            print("Port 6 is usually reserved for OLED screens and light sensors. Please consider other ports \
                  (Port 3 recommended).")

        NeoPixel.__init__(self, pin = Pin(PORT_MAPPING[port]), n=n)

    def on(self):
        blue_modulo = 3
        for i in range(self.n):
            NeoPixel.__setitem__(self, i, (255, 0, 0))
            if i % blue_modulo == 0:
                NeoPixel.__setitem__(self, i, (61, 0, 255))
        NeoPixel.write(self)

    def off(self):
        NeoPixel.fill(self, (0, 0, 0))
        NeoPixel.write(self)