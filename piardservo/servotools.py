import piardservo.servos_base as base


def degree_to_pulse_width(pos, o_range, s_range=(0, 180)):
    """
    converts degrees to the corresponding microsecond values
    """
    o_min, o_max = o_range
    s_min, s_max = s_range

    return o_min + pos / (s_max-s_min) * (o_max-o_min)


class BoundedServoParamList(list):
    """
    helper data structure (inherets from list) for storing angle values that are within
    specified angle ranges.

    example for controller.a_range = [[0, 180], [70, 130]

    >>> angles = BoundedServoParamList([90, 90], controller)
    >>> angles[0] = 40000
    >>> print(angles)
    [180, 90]
    >>> angles[1] = 30
    >>> print(angles)
    [180, 70]

    """

    def __init__(self, data, controller):

        super().__init__(data)

        assert issubclass(controller, base.ServoController)
        self.controller = controller
        for i, v in enumerate(self):
            self[i] = v

    def __setitem__(self, idx, value):

        # allows for slicing when setting values
        # such as:
        #
        # angles[:] = [...]
        # angles[3:4] = [1, 2]
        # angles[::2] = [...]
        #
        if isinstance(idx, slice):
            i_start = 0 if idx.start is None else idx.start
            i_stop = len(self) if idx.stop is None else idx.stop
            i_step = 1 if idx.step is None else idx.step
            idx = [i for i in range(i_start, i_stop, i_step)]

        if isinstance(idx, int):
            idx, value = [idx], [value]

        for i, v in zip(idx, value):
            assert v is not True and isinstance(v, (float, int))

            min_val, max_val = self.controller.a_range[i]

            if v < min_val:
                val = min_val
            elif v > max_val:
                val = max_val
            else:
                val = v

            list.__setitem__(self, i, val)


def servo_param_setter(n, min_max):
    assert isinstance(min_max, (float, int, list, tuple))
    # if max_max is a number
    if isinstance(min_max, (float, int)):
        return [min_max]*n
    # if it's a number in a tuple or list form
    elif isinstance(min_max, (list, tuple)) and len(min_max)==1:
        return [min_max[0]]*n

    elif len(min_max)==n:
        for mm in min_max:
            assert isinstance(mm, (float, int))
        return min_max
    else:
        assert isinstance(min_max[0], (float, int))
        out = [min_max[0]]*n
        for mm in min_max[1:]:
            assert len(mm)==2 and isinstance(mm[1], (float, int))
            out[mm[0]]=mm[1]
        return out
