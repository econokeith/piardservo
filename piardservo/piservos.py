try:
    import gpiozero
except Exception as exc:
    print("Raspberry Pi Dependency, gpiozero, Not Found")
    raise

try:
    from gpiozero.pins.pigpio import PiGPIOFactory
except Exception as exc:
    print("Raspberry Pi Dependency, pigpio, Not Found")
    raise

from piardservo.servos_base import ServoController
from piardservo.servotools import degree_to_pulse_width

class RPiServo(ServoController):

    def __init__(self,
                 address=None,
                 pins=(17,22),
                 **kwargs
                 ):

        self.address = address

        if isinstance(pins, int):
            n = 1
        else:
            n = len(pins)

        super().__init__(n=n, **kwargs)

        self.servos = []
        self.pins = pins
        self.initial_values = self.values

        if self._connect is True:
            self.connect(pins)

    def connect(self, pins=None):

        self.factory = PiGPIOFactory(host=self.address)
        _pins = self.pins if pins is None else pins

        for i, pin in enumerate(_pins):
            servo = gpiozero.Servo(pin,
                                   pin_factory=self.factory,
                                   min_pulse_width = self.min_pulse_width[i]/1000000,
                                   max_pulse_width = self.max_pulse_width[i]/1000000,
                                   initial_value = self.initial_values[i]
                                   )

            self.servos.append(servo)

    @property
    def is_open(self):
        for i, servo in enumerate(self.servos):
            if servo.closed is True:
                return False

        return True

    def close(self):
        self.factory.close()

    def write(self):
        for servo, value, flip in zip(self.servos, self.values, self.flip):
            servo.value = value * (-1) ** flip
