import abc

from piardservo.servotools import BoundedServoParamList, servo_param_setter, linear_transform


class ServoController(abc.ABC):

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
            assert (max_a - min_a) <= sr

        self.angle_format = angle_format

        if self.angle_format == 'minus_to_plus':
            self.center_angle = [0] * n
            self.servo_min = [-sr//2 for sr in self.servo_range]
            self.servo_max = [sr//2 for sr in self.servo_range]

        else:
            self.center_angle = [sr // 2 for sr in self.servo_range]
            self.servo_min = [0]*self.n
            self.servo_max = [sr for sr in self.servo_range]

        self._center_angle_offset = [0] * n
        self.update_center_offset(servo_param_setter(n, center_angle_offset))

        self.min_pulse_width = servo_param_setter(n, min_pulse_width)
        self.max_pulse_width = servo_param_setter(n, max_pulse_width)
        self.step_size = servo_param_setter(n, step_size)
        self.flip = servo_param_setter(n, flip)

        self._angles = BoundedServoParamList(self.initial_angle, self)

    @property
    def n(self):
        return self._n

    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, new_angles):
        self._angles[:] = servo_param_setter(self.n, new_angles, self._angles)

    @property
    def pulse_widths(self):
        out = []
        for a, s_max, s_min, max_pw, min_pw, flip in zip(self._angles,
                                                         self.servo_min,
                                                         self.servo_max,
                                                         self.max_pulse_width,
                                                         self.min_pulse_width,
                                                         self.flip,
                                                         ):

            pw = linear_transform(a, (s_min, s_max), (min_pw, max_pw), flip)
            out.append(pw)
        return out

    @pulse_widths.setter
    def pulse_widths(self, pulses):
        pws = self.pulse_widths
        pws = servo_param_setter(self.n, pulses, pws)
        new_angles = []
        for pw, s_max, s_min, max_pw, min_pw, flip in zip(pws,
                                                          self.servo_max,
                                                          self.servo_min,
                                                          self.max_pulse_width,
                                                          self.min_pulse_width,
                                                          self.flip,
                                                          ):

            a = linear_transform(pw, (min_pw, max_pw), (s_min, s_max), flip)
            new_angles.append(a)
        self._angles[:] = new_angles

    @property
    def values(self):
        _values = []
        for a, s_min, s_max, flip in zip(self._angles,
                                         self.servo_min,
                                         self.servo_max,
                                         self.flip
                                         ):

            val = linear_transform(a, (s_min, s_max), (-1, 1), flip)
            _values.append(val)

        return _values

    @values.setter
    def values(self, new_values):
        _values = self.values
        _values = servo_param_setter(self.n, new_values, _values)
        new_angles = []
        for v, s_min, s_max, flip in zip(_values,
                                         self.servo_min,
                                         self.servo_max,
                                         self.flip
                                         ):

            a = linear_transform(v, (-1, 1), (s_min, s_max), flip)
            new_angles.append(a)
        self._angles[:] = new_angles

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
            self.servo_min[i] -= diff[i]
            self.servo_max[i] -= diff[i]

        self._center_angle_offset = new_offset

    def reset(self):
        self._angles = self.initial_angle
        self.write()

    def move(self, moves, write=True):
        assert len(moves) == self.n
        for i, m in enumerate(moves):
            self.angles[i] += m * (-1) ** self.flip[i]

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
