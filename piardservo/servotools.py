# import piardservo.servos_base as base


def degree_to_pulse_width(pos, o_range, s_range=(0, 180)):
    """
    converts degrees to the corresponding microsecond values
    """
    o_min, o_max = o_range
    s_min, s_max = s_range

    return o_min + pos / (s_max-s_min) * (o_max-o_min)


def linear_transform(x, range_0, range_1, flip=0):

    min0, max0 = range_0

    if flip == 0:
        min1, max1 = range_1
    else:
        max1, min1 = range_1

    return (x - min0)/(max0-min0)*(max1-min1) + min1



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

        #assert issubclass(controller, base.ServoController)
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

#todo turn the asserts into raises
def servo_param_setter(n,
                       param_values,
                       old_values=None
                       ):

    assert isinstance(param_values, (float, int, list, tuple))
    # if max_max is a number
    if isinstance(param_values, (float, int)):
        return [param_values] * n

    elif isinstance(param_values, (list, tuple)) and len(param_values)==n:
        for p_value in param_values:
            assert isinstance(p_value, (float, int))
        return param_values

    elif isinstance(param_values, (list, tuple)) and isinstance(param_values[0], (int, float)):
        out = [param_values[0]] * n
        for p_value in param_values[1:]:
            assert len(p_value) == 2 and isinstance(p_value[1], (float, int))
            out[p_value[0]] = p_value[1]
        return out

    elif isinstance(param_values, (list, tuple)) and old_values is not None:
        for p_value in param_values:
            old_values[p_value[0]] = old_values[p_value[1]]
        return old_values

    else:
        raise Exception('Inputs not of the proper form')
