import gc
from machine import Pin, PWM
from wio_link import PORT_MAPPING, DEFAULT_PORTS, GroveDevice
gc.collect()

class Actuator(GroveDevice):

    def check_port(self, type, port):

        if port == 3:
            raise OSError("{0}s cannot be connected to Port 3. Please try Ports 1, 2".format(type))
        elif port == 4:
            raise OSError("Port 4 is an analog port.  Please try Ports 1, 2")
        elif port == 6:
            print("Port 6 is usually reserved for OLED screens and light sensors. Please consider other ports.")

    def __init__(self, type, port):
        GroveDevice.__init__(self, type, port)
        self.check_port(type, port)


def degree2duty(degree, start=35, end=132): 

    if degree < 0 or degree > 180:
        raise ValueError("Please choose a degree between 0 and 180")
    return int(start + (end - start) * (degree / 180))


class Servo(Actuator):

    def __init__(self, port=DEFAULT_PORTS["Servo"], position=0):
        Actuator.__init__(self, "Servo", port)
        self.servo = PWM(Pin(PORT_MAPPING[port]), duty=degree2duty(position), freq=50)
        self.position = position

    def set_position(self, degree):
        self.servo.duty(degree2duty(degree))
        self.position = degree

    def get_position(self):
        return self.position


class Relay(Actuator):

    def __init__(self, port=DEFAULT_PORTS["Relay"]):
        Actuator.__init__(self, "Relay", port)
        self.relay = Pin(PORT_MAPPING[port], Pin.OUT)
        
    def on(self):
        self.relay.on()

    def off(self):
        self.relay.off()

    def get_status(self):
        return self.relay.value()


class Button(Actuator):
    def __init__(self, port=DEFAULT_PORTS["Button"]):
        Actuator.__init__(self, "Button", port)
        self.pin = Pin(PORT_MAPPING[port], Pin.IN, Pin.PULL_UP)

    def is_pressed(self):
        return True if self.pin.value() == 1 else False

    def on_press(self, callback):
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=callback)

    def on_release(self, callback):
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)