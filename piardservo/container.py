import abc

from piardservo.servotools import servo_param_setter
from piardservo.servo_object import ServoObject


class ServoContainer(abc.ABC):

    def __init__(self,
                 n=1,
                 min_angle=-90,
                 max_angle=90,
                 initial_angle=0,
                 center_angle_offset=0,
                 angle_format='minus_to_plus',
                 flip=0,
                 servo_range=180,
                 step_size=1,
                 min_pulse_width=1000,
                 max_pulse_width=2000,
                 connect=True,
                 microcontroller=None
                 ):

        self._n = n
        self._connect = connect
        self.angle_format = angle_format
        self.microcontroller = microcontroller

        _min_angle = servo_param_setter(n, min_angle)
        _max_angle = servo_param_setter(n, max_angle)
        _initial_angle = servo_param_setter(n, initial_angle)
        _servo_range = servo_param_setter(n, servo_range)
        _update_center_offset = servo_param_setter(n, center_angle_offset)
        _min_pulse_width = servo_param_setter(n, min_pulse_width)
        _max_pulse_width = servo_param_setter(n, max_pulse_width)
        _step_size = servo_param_setter(n, step_size)
        _flip = servo_param_setter(n, flip)

        self.servos = []

        for i in range(n):
            servo = ServoObject(i=i,
                                min_angle=_min_angle[i],
                                max_angle=_max_angle[i],
                                initial_angle=_initial_angle[i],
                                center_angle_offset=_update_center_offset[i],
                                angle_format=angle_format,
                                flip=_flip[i],
                                servo_range=_servo_range[i],
                                step_size=_step_size[i],
                                min_pulse_width=_min_pulse_width[i],
                                max_pulse_width=_max_pulse_width[i]
                                )

            self.servos.append(servo)

    def __getitem__(self, i):
        return self.servos[i]

    def __len__(self):
        return self.n

    @property
    def n(self):
        return self._n

    def angles(self):
        return tuple([servo.angle for servo in self.servos])

    def values(self):
        return tuple([servo.value for servo in self.servos])

    def pulse_widths(self):
        return tuple([servo.pulse_width for servo in self.servos])

    def show(self, name):
        out = []
        for servo in self.servos:
            out.append(getattr(servo, name))
        return tuple(out)

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def write(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass

