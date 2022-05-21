import abc

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

class MicroController(abc.ABC):

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def write(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

class RPiWifi(MicroController):

    def __init__(self,
                 address=None,
                 pins=(17,22),
                 container = None
                 ):

        self.address = address
        self.container = container

        if isinstance(pins, int):
            n = 1
        else:
            n = len(pins)

        self.pins = pins
        self.n = n

        self._servos = []

    def connect(self, pins=None):

        if self.address is not None:
            self.factory = PiGPIOFactory(host=self.address)
        else:
            raise Exception("no address for Raspberry Pi")

        if self._servos:
            for _servo in self._servos:
                _servo.close()
            self._servos = []

        if self.container is not None:
            _pins = self.pins if pins is None else pins

            min_pws = self.container.show('min_pulse_width')
            max_pws = self.container.show('max_pulse_width')
            ivs = self.container.values()


            for i, pin in enumerate(_pins):
                servo = gpiozero.Servo(pin,
                                       pin_factory=self.factory,
                                       min_pulse_width=min_pws[i] / 1000000,
                                       max_pulse_width=max_pws[i] / 1000000,
                                       initial_value=ivs[i]
                                       )

                self._servos.append(servo)

    def write(self):
        for i, servo in enumerate(self.container.servos):
            if servo._written is False:
                self._servos[i].value = servo.value
                servo._written = True

    def close(self):
        self.factory.close()



