"""
Due to limitations from the arcade library, the fn key does not work.
"""
from typing import Union, Tuple, List, Dict

import arcade

from key import *
from key import _kn2v, _kv2n

sep = 0.075
SCALING = 3 / sep


class Key:
    def __init__(self, width: float, height: float, symbol: int,
                 center_x: float = 0, center_y: float = 0):
        self.width = width
        self.height = height
        self.symbol = symbol
        self.position = (center_x, center_y)

    def __str__(self):
        return f"{self.width} {self.height} {self.symbol} {self.position}"

    @property
    def center_x(self):
        return self.position[0]

    @property
    def center_y(self):
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
        if i == 0:
            keys[i].position = first_posn
            continue
        self = keys[i]
        prev = keys[i-1]
        self.position = (round(prev.center_x + prev.width / 2 + self.width / 2 + sep, 10), first_posn[1])


def _create_small_notebook_keys(verbose=False) -> Dict[int, Key]:

    size_normal_keys = (1.125, 1.125)
    size_f_keys = (1.075, 0.725)
    size_arrow_keys = (1.075, 0.525)

    key_plan = [[LCTRL, FN, LWINDOWS, LALT, SPACE, RALT, RCTRL],
                [LSHIFT, Z, X, C, V, B, N, M, COMMA, PERIOD, SLASH, RSHIFT],
                [CAPSLOCK, A, S, D, F, G, H, J, K, L, SEMICOLON, APOSTROPHE, ENTER],
                [TAB, Q, W, E, R, T, Y, U, I, O, P, BRACKETLEFT, BRACERIGHT, BACKSLASH],
                [GRAVE, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0, MINUS, EQUAL, BACKSPACE],
                [ESCAPE, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, INSERT, DELETE]]
    special_key_sizes = [{'SPACE': (6.525, 1.125)},
                         {'LSHIFT': (2.325, 1.125), 'RSHIFT': (2.775, 1.125)},
                         {'CAPSLOCK': (1.725, 1.125), 'ENTER': (2.175, 1.125)},
                         {'TAB': (1.425, 1.125), 'BACKSLASH': (1.275, 1.125)},
                         {'GRAVE': (0.825, 1.125), 'BACKSPACE': (1.875, 1.125)},
                         {}]

    out = []
    # create keys in row 0-4
    for i in range(5):
        temp = _create_keys(key_plan[i], *size_normal_keys, **special_key_sizes[i])
        _init_key_posn(temp, (temp[0].width / 2, temp[0].height / 2 + i * 1.2))
        out += temp
        if verbose:
            [print(key) for key in temp]
            print()
    # create F keys (row 5)
    temp = _create_keys(key_plan[5], *size_f_keys)
    _init_key_posn(temp, (temp[0].width / 2, 6.3625))
    out += temp
    if verbose:
        [print(key) for key in temp]
        print()
    # create arrow keys
    temp = _create_keys([LEFT, DOWN, RIGHT, UP], *size_arrow_keys)
    _init_key_posn(temp[:3], (14.3375, size_arrow_keys[1] / 2))
    temp[3].position = (round(14.3375 + size_arrow_keys[0] + sep, 10), 0.8625)
    out += temp
    if verbose:
        [print(key) for key in temp]
        print()

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


class KeyboardModel:
    """ Representation of a keyboard without graphics """
    def __init__(self, type='small notebook'):
        self.keys = {'small notebook': _create_small_notebook_keys,
                     'large notebook': _create_large_notebook_keys,
                     'mechanical': _create_mechanical_keys}[type]()
        self.width, self.height = {'small notebook': (18.05, 7.6),
                                   'large notebook': (22.85, 7.6),
                                   'mechanical': (23.4, 9.0)}[type]
        self.scaling = SCALING


class ShapeGroup:
    def __init__(self, shapes: List[arcade.Shape], center_x: float = None, center_y: float = None, **kwargs):
        if center_x is None or center_y is None:
            # TODO find center and boundary of overall shape
            raise NotImplementedError
        else:
            self.position = (center_x, center_y)
        self._shapes = shapes
        self.width = kwargs.pop('width', 1)
        self.height = kwargs.pop('height', 1)

    def draw(self):
        for shape in self._shapes:
            shape.draw()


def create_keyboard_shape(center_x: float, center_y: float) -> ShapeGroup:
    keyboard = KeyboardModel()
    width, height = keyboard.width, keyboard.height
    keys = keyboard.keys
    bounding_box = arcade.create_rectangle_filled(center_x, center_y,
                                                  width*SCALING, height*SCALING, color=arcade.color.DARK_BLUE_GRAY)
    shapes = [bounding_box]
    origin = (center_x - (width/2 - .4375)*SCALING, center_y - (height/2 - .4375)*SCALING)
    for key in keys.values():
        temp = arcade.create_rectangle_filled(origin[0] + key.center_x*SCALING, origin[1] + key.center_y*SCALING,
                                              key.width*SCALING, key.height*SCALING, color=arcade.color.LIGHT_BLUE)
        shapes.append(temp)
    return ShapeGroup(shapes, center_x, center_y, width=width, height=height)



