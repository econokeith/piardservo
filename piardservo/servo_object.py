from piardservo.servotools import linear_transform


class ServoObject:

    def __init__(self,
                 i=1,
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
                 write_on_update = False,
                 container = None
                 ):

        self._i = i

        self.min_angle = min_angle
        self.max_angle = max_angle
        self.initial_angle = initial_angle
        self.servo_range = servo_range
        self.write_on_update = write_on_update
        self.container = container

        if (max_angle - min_angle) > servo_range:
            raise ValueError("Max Angle - Min Angle > Servo Range")

        self.angle_format = angle_format

        if self.angle_format == 'minus_to_plus':
            self.center_angle = 0
            self.servo_min = -servo_range//2
            self.servo_max = servo_range//2

        else:
            self.center_angle = self.servo_range//2
            self.servo_min = 0
            self.servo_max = servo_range

        self._center_angle_offset = 0
        self.center_angle_offset = center_angle_offset

        self._min_pulse_width = min_pulse_width
        self._max_pulse_width = max_pulse_width

        self.step_size = step_size
        self.flip = flip

        self._angle = self.initial_angle

        self._pulse_width = self.__measure_convert(self._angle, 'angle', 'pulse_width')
        self._value = self.__measure_convert(self._angle, 'angle', 'value')
        self._written = True

    @property
    def i(self):
        return self._i

    @property
    def min_pulse_width(self):
        return self._min_pulse_width

    @min_pulse_width.setter
    def min_pulse_width(self, pw):
        self._min_pulse_width = pw

    @property
    def max_pulse_width(self):
        return self._max_pulse_width

    @max_pulse_width.setter
    def max_pulse_width(self, pw):
        self._max_pulse_width = pw

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, new_angle):

        if new_angle >= self.max_angle:
            self._angle = self.max_angle
        elif new_angle <= self.min_angle:
            self._angle = self.min_angle
        else:
            self._angle = new_angle

        self._written = False

        if self.write_on_update is True and self.container is not None:
            self.container.microcontroller.write()

    @property
    def pulse_width(self):
        return self.__measure_convert(self._angle, 'angle', 'pulse_width')

    @pulse_width.setter
    def pulse_width(self, pw):
        self.angle = self.__measure_convert(pw, 'pulse_width', 'angle')

    @property
    def value(self):
        return self.__measure_convert(self._angle, 'angle', 'value')

    @value.setter
    def value(self, v):
        self.angle = self.__measure_convert(v, 'value', 'angle')

    @property
    def center_angle_offset(self):
        return self._center_angle_offset

    @center_angle_offset.setter
    def center_angle_offset(self, new_offset):
        diff = new_offset - self._center_angle_offset
        self.min_angle -= diff
        self.max_angle -= diff
        self.initial_angle -= diff
        self.center_angle -= diff
        self.servo_min -= diff
        self.servo_max -= diff
        self._center_angle_offset = new_offset

    def reset(self):
        self.angles = self.initial_angle

    def min(self):
        self.angles = self.min_angle

    def mid(self):
        self.angles = self.center_angle

    def max(self):
        self.angles = self.max_angle

    def __get_range(self, measure):
        if measure == 'value':
            return -1, 1
        elif measure == 'pulse_width':
            return self.min_pulse_width, self.max_pulse_width
        else:
            return self.servo_min, self.servo_max

    def __measure_convert(self, x, m0, m1, flip=None):
        r0 = self.__get_range(m0)
        r1 = self.__get_range(m1)
        _flip = self.flip if flip is None else flip
        return linear_transform(x, r0, r1, _flip)







