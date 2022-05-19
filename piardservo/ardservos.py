from piardservo.ard_helpers.connection import ArduinoSerialPort
from piardservo.ard_helpers.encoders import CommaDelimitedEncoder
from piardservo.servos_base import ServoController

class ArduinoServo(ServoController):

    def __init__(self,
                 n=1,
                 address=3,
                 baud=9600,
                 time_out=1,
                 **kwargs
                 ):

        super().__init__(n, **kwargs)

        self.connection = ArduinoSerialPort(address, baud, time_out=time_out)

        if self._connect is True:
            self.connection.connect()

        self.encoder = CommaDelimitedEncoder()

    @property
    def is_open(self):
        return self.connection.is_open

    def write(self, *args, **kwargs):
        data = self.pulse_widths
        data = [int(d) for d in data]
        message = self.encoder.encode_data(data)
        self.connection.write(message)

    def connect(self, *args, **kwargs):
        self.connection.connect(*args, **kwargs)

    def move(self, moves, write=True):
        assert len(moves)==self.n
        for i, m in enumerate(moves):
            self.angles[i] += m * (-1)**self.flip[i]

        if write is True:
            self.write()

    def close(self):
        self.connection.close()
