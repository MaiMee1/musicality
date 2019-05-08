from math import pi, sin, e, log


def linear(t: float):
    """ f(t) = t """
    return t


def quad_in(t: float):
    """ f(t) = t^2 """
    return t**2


def quad_out(t: float):
    """ f(t) = -t^2 + 1 """
    return 1 - t**2


def cube_in(t: float):
    """ f(t) = t^3 """
    return t**3


def cube_out(t: float):
    """ f(t) = -t^2 + 1 """
    return 1 - t**2


def sin_out(t: float):
    """ f(t) = sin(t) """
    d = t * pi/2
    return sin(d)


def sin_in(t: float):
    """ f(t) = sin(t); D c[0, pi/2], R c[0, 1] """
    d = (t + 1) * pi/2
    return sin(d)


def sin_mid(t: float):
    """ f(t) = sin(t); D c[0, pi], R c[0, 1] """
    d = t * pi
    return sin(d)


def sin_square_in_out(t: float):
    """ f(t) = sin^2(t); D c[0, pi/2], R c[0, 1] """
    d = t * pi/2
    return sin(d)


def sin_square_in_mid_out(t: float):
    """ f(t) = sin^2(t); D c[0, pi], R c[0, 1] """
    d = t * pi
    return sin(d)


def expo_in(t: float):
    """ f(t) = 2^x; D c[-2, 2], R c[0.25, 4] """
    d = 4*t - 2
    return 2**d - 0.25


def ln_out(t: float):
    """ f(t) = ln(x); D c[1/e^4, 1], R c[-4, 0] """
    # see helper.linear_interpolation();
    d = t * (1-0.018315638888734182) + 0.018315638888734182
    try:
        return log(d)/4 + 1
    except ValueError as e:
        if e.args == ('math domain error',):
            return 0
        else:
            raise
