"""
Due to limitations from the arcade library, the fn key does not work.
"""
from typing import Union, Tuple, List, Dict

from key import *
from key import _kn2v, _kv2n

sep = 0.075
SCALING = 2 / sep


class Key:
    def __init__(self, width: float, height: float, symbol: int,
                 center_x: float = 0, center_y: float = 0):
        self.width = width
        self.height = height
        self.symbol = symbol
        self.position = (center_x, center_y)

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]


def _create_keys(keys: List[int], width: float, height: float, **kwargs) -> List[Key]:
    out = []
    for key in keys:
        if _kv2n(key) in kwargs:
            size = kwargs[_kv2n(key)]
            assert isinstance(size, tuple)
            out.append(Key(size[0], size[1], symbol=key))
        else:
            out.append(Key(width, height, symbol=key))
    return out


def _init_key_posn(keys: List[Key], first_posn: Tuple[float, float]):
    for i in range(len(keys)):
        if i == 1:
            keys[i].position = first_posn
        self = keys[i]
        prev = keys[i-1]
        self.position = (prev.x + prev.width / 2 + self.width / 2 + sep, first_posn[1])


def _create_small_notebook_keys() -> Dict[int, Key]:

    size_normal_keys = (1.125, 1.125)
    size_f_keys = (1.075, 0.725)
    size_arrow_keys = (1.075, 0.525)

    key_plan = [[LCTRL, LWINDOWS, LALT, SPACE, RALT, RWINDOWS, MENU, RCTRL],
                [LSHIFT, Z, X, C, V, B, N, M, COMMA, PERIOD, SLASH, RSHIFT],
                [CAPSLOCK, A, S, D, F, G, H, J, K, L, SEMICOLON, APOSTROPHE, ENTER],
                [TAB, Q, W, E, R, T, Y, U, I, O, P, BRACKETLEFT, BRACERIGHT, BACKSLASH],
                [GRAVE, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0, MINUS, EQUAL, BACKSPACE],
                [ESCAPE, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12]]
    special_key_sizes = [{'SPACE': (6.525, 1.125)},
                         {'LSHIFT': (2.325, 1.125), 'RSHIFT': (2.775, 1.125)},
                         {'CAPSLOCK': (1.725, 1.125), 'ENTER': (2.175, 1.125)},
                         {'TAB': (1.425, 1.125), 'BACKSLASH': (1.425, 1.125)},
                         {'GRAVE': (1.275, 1.125), 'BACKSPACE': (1.275, 1.125)},
                         {}]

    out = []
    # create keys in row 0-4
    for i in range(5):
        temp = _create_keys(key_plan[i], *size_normal_keys, **special_key_sizes[i])
        _init_key_posn(temp, (temp[0].width / 2, temp[0].height / 2 + i * sep))
        out.append(*temp)
    # create F keys (row 5)
    temp = _create_keys(key_plan[5], *size_f_keys)
    _init_key_posn(temp, (temp[0].width / 2, temp[0].height / 2 + 5 * sep))
    out.append(*temp)
    # create arrow keys
    temp = _create_keys([LEFT, DOWN, RIGHT, UP], *size_arrow_keys)
    _init_key_posn(temp[:3], (14.3375, size_arrow_keys[1] / 2))
    temp[3].position = (14.3375 + size_arrow_keys[0] + sep, size_arrow_keys[1] + sep)
    out.append(*temp)

    d = {}
    for elem in out:
        d[elem.symbol] = elem
    return d


def _create_large_notebook_keys() -> Dict[int, Key]:
    raise NotImplementedError


def _create_mechanical_keys() -> Dict[int, Key]:
    # row_0 = [LCTRL, LWINDOWS, LALT, SPACE, RALT, RWINDOWS, MENU, RCTRL]
    # row_1 = [LSHIFT, Z, X, C, V, B, N, M, COMMA, PERIOD, SLASH, RSHIFT]
    # row_2 = [CAPSLOCK, A, S, D, F, G, H, J, K, L, SEMICOLON, APOSTROPHE, ENTER]
    # row_3 = [TAB, Q, W, E, R, T, Y, U, I, O, P, BRACKETLEFT, BRACERIGHT, BACKSLASH]
    # row_4 = [GRAVE, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0, MINUS, EQUAL, BACKSPACE]
    # row_5 = [ESCAPE, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12]
    # center_cluster = [PRINT, SCROLLLOCK, PAUSE,
    #                   INSERT, HOME, PAGEUP,
    #                   DELETE, END, PAGEDOWN]
    # arrow_keys = [LEFT, DOWN, RIGHT, UP]
    raise NotImplementedError


class Keyboard:
    """ Representation of a keyboard without graphics """
    def __init__(self, width: float, height: float,
                 center_x: float = 0, center_y: float = 0,
                 type='small notebook'):
        self.width = width
        self.height = height
        self.position = (center_x, center_y)
        self.keys = {'small notebook': _create_small_notebook_keys,
                     'large notebook': _create_large_notebook_keys,
                     'mechanical': _create_mechanical_keys}[type]()
        self.scaling = SCALING

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]
