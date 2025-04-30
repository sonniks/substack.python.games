# utils/helpers.py


def clamp(value, minimum, maximum):
    """
    Clamp a value between a minimum and maximum range.
    :param value:
    :param minimum:
    :param maximum:
    :return:
    """
    return max(minimum, min(value, maximum))


def lerp(start, end, t):
    """
    Linearly interpolate between two values based on a parameter t.
    :param start:
    :param end:
    :param t:
    :return:
    """
    return start + t * (end - start)
