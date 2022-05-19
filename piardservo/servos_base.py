import abc
#in case people only need the arduino controller
from piardservo.piservos import RPiServo
from piardservo.servotools import BoundedServoParamList, servo_param_setter




class ServoController(abc.ABC):

    def __init__(self,
                 n=1,
                 min_angle = -90,
                 max_angle = 90,
                 initial_angle= 0,
                 center_angle_offset = 0,
                 angle_format='minus_to_plus',
                 servo_range=180,
                 step_size=1,
                 flip=0,
                 min_pulse_width=1000,
                 max_pulse_width=2000,
                 connect=True
                 ):

        self._n = n
        self._connect = connect

        self.min_angle = servo_param_setter(n, min_angle)
        self.max_angle = servo_param_setter(n, max_angle)
        self.initial_angle = servo_param_setter(n, initial_angle)
        self.servo_range = servo_param_setter(n, servo_range)

        for min_a, max_a, sr in zip(self.min_angle,
                                    self.max_angle,
                                    self.servo_range):
            assert (max_a-min_a) <= sr

        if angle_format == 'minus_to_plus':
            self.center_angle = [0] * n
            self._abs_fix = 0
        else:
            self.center_angle = [sr // 2 for sr in self.servo_range]

        self._center_angle_offset = [0] * n
        self.update_center_offset(servo_param_setter(n, center_angle_offset))

        self.min_pulse_width = servo_param_setter(n, min_pulse_width)
        self.max_pulse_width = servo_param_setter(n, max_pulse_width)
        self.step_size = servo_param_setter(n, step_size)
        self.flip = servo_param_setter(n, flip)

        self._abs_angles = BoundedServoParamList(self.initial_angle, self)

    @property
    def n(self):
        return self._n

    @property
    def angles(self):
        return self._abs_angles

    @angles.setter
    def angles(self, new_angles):
        assert isinstance(new_angles, (tuple, list))
        assert len(new_angles) == self.n
        self._abs_angles[:] = new_angles

    @property
    def pulse_widths(self):
        out = []
        for a, sr, max_pw, min_pw in zip(self._abs_angles,
                                         self.servo_range,
                                         self.max_pulse_width,
                                         self.min_pulse_width):

            pw = a / sr * (max_pw-min_pw)
            out.append(pw)
        return out

    @property
    def values(self):
        out = []
        for a, sr, max_pw, min_pw in zip(self._abs_angles,
                                         self.servo_range,
                                         self.max_pulse_width,
                                         self.min_pulse_width):

            val = a / sr * 2 - 1
            out.append(val)

        return out

    @property
    def center_angle_offset(self):
        return self._center_angle_offset

    @center_angle_offset.setter
    def center_angle_offset(self, value):
        raise Exception("use the update_center_offset() method instead")

    def update_center_offset(self, offset):
        new_offset = servo_param_setter(self.n, offset)
        old_offset = self._center_angle_offset
        diff = [n-o for o, n in zip(old_offset, new_offset)]

        for i in range(self.n):
            self.min_angle[i] -= diff[i]
            self.max_angle[i] -= diff[i]
            self.initial_angle[i] -= diff[i]
            self.center_angle[i] -= diff[i]

        self._center_angle_offset = new_offset

    def reset(self):
        self._abs_angles = self.initial_angle
        self.write()

    def move(self, moves, write=True):
        assert len(moves)==self.n
        for i, m in enumerate(moves):
            self.angles[i] += m * (-1)**self.flip[i]

        if write is True:
            self.write()

    @property
    @abc.abstractmethod
    def is_open(self):
        pass

    @abc.abstractmethod
    def write(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def connect(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def close(self):
        pass




