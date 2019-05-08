from typing import Union, Tuple

from game.animation.base import EasingBase
from game.animation.easefunc import linear, quad_in, quad_out, sin_in, sin_out, sin_mid, sin_square_in_out, sin_square_in_mid_out, \
    expo_in, ln_out

RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
Color = Union[RGB, RGBA]


def filter_color(color) -> RGBA:
    """ Given unknown input return RGBA or raise ValueError """
    try:
        if len(color) == 3:
            r, g, b = color
            a = 255
        elif len(color) == 4:
            r, g, b, a = color
        else:
            raise ValueError('color must be in color format')
    except TypeError:
        raise
    assert 0 <= r <= 255
    assert 0 <= g <= 255
    assert 0 <= b <= 255
    assert 0 <= a <= 255
    return r, g, b, a


class ColorChange(EasingBase):
    """ Change color """

    def func(self, t: float, **kwargs) -> Color:
        """Return eased color

        :param t:
        :param kwargs: color1, color2
        :return: eased color (Color)
        """
        color1, color2 = kwargs.pop('color1', None), kwargs.pop('color2', None)
        assert color1 is not None, 'specify color1'
        assert color2 is not None, 'specify color2'
        r1, g1, b1, a1 = filter_color(color1)
        r2, g2, b2, a2 = filter_color(color2)
        r = r1 + round((r2 - r1) * t)
        g = g1 + round((g2 - g1) * t)
        b = b1 + round((b2 - b1) * t)
        a = a1 + round((a2 - a1) * t)
        return r, g, b, a

    def ease(self, t: float) -> float:
        return quad_out(t)

