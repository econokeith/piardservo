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
                 factory = None,
                 **kwargs):

        if isinstance(pins, int):
            n = 1
        else:
            n = len(pins)

        super().__init__(n=n, **kwargs)

        if factory is None:
            self.factory = PiGPIOFactory(host=address)
        else:
            self.factory = factory

        self.servos = []
        self.pins = pins
        self.initial_values = self.values

        if self._connect is True:
            self.connect(pins)


    def connect(self, pins=None):
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
        for servo in self.servos:
            servo.close()
        self.servos = []

    def write(self):
        for i, servo in enumerate(self.servos):
            servo.value = degree_to_pulse_width(self.angles[i], (-1, 1))

def main():
    import time
    Servo = RPiServo('192.168.1.28')
    print(Servo.is_open)
    for i in range(4):
        Servo.move((10*-1**i, 10*-1**i))
        time.sleep(1)

    Servo.close()


if __name__=='__main__':
    main()

