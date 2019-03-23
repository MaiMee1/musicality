"""
Due to limitations from the arcade library, the FN key does not work.
Due to some bindings, RSHIFT registers as LSHIFT in this laptop's keyboard.
EDIT: And also others. Seems to be the way library checks instead.
"""
from typing import Dict
from typing import NewType

import arcade
from arcade.arcade_types import *

import key

Drawable = NewType('Drawable', Union[arcade.Shape, arcade.Shape, arcade.ShapeElementList, 'Rectangle'])

SCALING_CONSTANT = 1
SEP = 0.075
SCALING = SCALING_CONSTANT / SEP
PRECISION = 10

COLOR_REC_DEFAULT = arcade.color.BLACK


def set_scaling(new_value):
    global SCALING_CONSTANT, SCALING
    SCALING_CONSTANT = new_value
    SCALING = SCALING_CONSTANT / SEP


class Rectangle:
    def __init__(self, center_x: float, center_y: float, width: float,
                 height: float, **kwargs):
        self.width = width
        self.height = height
        self._position = [center_x, center_y]

        self.color = kwargs.pop('color', COLOR_REC_DEFAULT)  # type: Color
        self.alpha = kwargs.pop('alpha', 255)  # type: int
        self.border_width = kwargs.pop('border_width', 1)  # type: float
        self.tilt_angle = kwargs.pop('tilt_angle', 0)  # type: float

        self.shape = None  # type: arcade.Shape

        self.update_rate = 1/60

    def __str__(self):
        return f"size: {self.size} posn: {self._position}"

    def _get_position(self) -> (float, float):
        return self._position[0], self._position[1]

    def _set_position(self, new_value: (float, float)):
        self._position = list(new_value)

    position = property(_get_position, _set_position)

    def _get_center_x(self) -> float:
        return self._position[0]

    def _set_center_x(self, new_value: float):
        self._position[0] = new_value

    center_x = property(_get_center_x, _set_center_x)

    def _get_center_y(self) -> float:
        return self._position[1]

    def _set_center_y(self, new_value: float):
        self._position[1] = new_value

    center_y = property(_get_center_y, _set_center_y)

    def move(self, delta_x: float, delta_y: float) -> (float, float):
        """ Return: new position """
        self.center_x += delta_x
        self.center_y += delta_y
        return self.position

    def _get_right(self) -> float:
        return self._position[0] + round(self.width / 2, PRECISION)

    def _set_right(self, new_value: float):
        self.center_x += new_value - round(self.width / 2, PRECISION) - self.center_x

    right = property(_get_right, _set_right)

    def _get_left(self) -> float:
        return self._position[0] - round(self.width / 2, PRECISION)

    def _set_left(self, new_value: float):
        self.center_x += new_value + round(self.width / 2, PRECISION) - self.center_x

    left = property(_get_left, _set_left)

    def _get_top(self) -> float:
        return self._position[1] + round(self.height / 2, PRECISION)

    def _set_top(self, new_value: float):
        self.center_y += new_value - round(self.height / 2, PRECISION) - self.center_y

    top = property(_get_top, _set_top)

    def _get_bottom(self) -> float:
        return self._position[1] - round(self.height / 2, PRECISION)

    def _set_bottom(self, new_value: float):
        self.center_y += new_value + round(self.height / 2, PRECISION) - self.center_y

    bottom = property(_get_bottom, _set_bottom)

    def _get_opacity(self) -> float:
        return round(self.alpha / 255, 1)

    def _set_opacity(self, new_value: float):
        self.alpha = int(round(new_value * 255, 0))

    opacity = property(_get_opacity, _set_opacity)

    @property
    def rgba_color(self) -> Color:
        return self.color[0], self.color[1], self.color[2], self.alpha

    @property
    def size(self) -> (float, float):
        return self.width, self.height

    def update(self):
        self.redraw()

    def redraw(self):
        self.shape = arcade.create_rectangle(self.center_x, self.center_y,
                                             self.width, self.height,
                                             self.rgba_color,
                                             tilt_angle=self.tilt_angle)

    def draw(self):
        self.shape.draw()

    def set_update_rate(self, rate: float):
        self.update_rate = rate


class Key(Rectangle):
    COLOR_PRESSED = arcade.color.WHITE, 255
    COLOR_NORMAL = arcade.color.BLACK, 150

    def __init__(self, center_x: float, center_y: float, width: float,
                 height: float, symbol: int, **kwargs):
        kwargs['color'], kwargs['alpha'] = Key.COLOR_NORMAL
        super().__init__(center_x, center_y, width, height, **kwargs)

        self.symbol = symbol
        self._to_draw = []  # type: List[arcade.Shape]

    def __str__(self):
        return f"key constant: {self.symbol} size: {self.size} posn: {self._position}"

    def on_key_press(self, symbol: int, modifiers: int):
        assert symbol == self.symbol
        self.color, self.alpha = Key.COLOR_PRESSED
        self.update()

    def on_key_release(self, symbol: int, modifiers: int):
        assert symbol == self.symbol
        self.color, self.alpha = Key.COLOR_NORMAL
        self.update()

    def come_in(self, delta_clock: float, rgba_color: Color):
        rgba_color = arcade.get_four_byte_color(rgba_color)
        # prep
        self._to_draw = []
        for i in range(1, int(delta_clock / self.update_rate) + 1):
            self._to_draw.append(arcade.create_rectangle(
                self.center_x, self.center_y,
                1 + (self.width - 1) * self.update_rate * i / delta_clock,
                1 + (self.height - 1) * self.update_rate * i / delta_clock,
                rgba_color,
                tilt_angle=self.tilt_angle))

    def draw(self):
        super().draw()
        if self._to_draw:
            self._to_draw.pop(0).draw()


def _align_center_x(shapes: List[Rectangle], index: int = 0, most=False) -> float:
    """ Returns center_x aligned to """
    if most:
        right = max([shape.right for shape in shapes])
        left = min([shape.left for shape in shapes])
        new_x = round((right + left) / 2, PRECISION)
    else:
        new_x = shapes[index].center_x
    for shape in shapes:
        shape.center_x = new_x
    return new_x


def _align_center_y(shapes: List[Rectangle], index: int = 0, most=False) -> float:
    """ Returns center_y aligned to """
    if most:
        top = max([shape.top for shape in shapes])
        bottom = min([shape.bottom for shape in shapes])
        new_y = round((top + bottom) / 2, PRECISION)
    else:
        new_y = shapes[index].center_y
    for shape in shapes:
        shape.center_y = new_y
    return new_y


def _align_right(shapes: List[Rectangle], index: int = 0, most=False) -> float:
    """ Returns center_x aligned to """
    if most:
        new_right = max([shape.right for shape in shapes])
    else:
        new_right = shapes[index].right
    for shape in shapes:
        shape.right = new_right
    return new_right


def _align_left(shapes: List[Rectangle], index: int = 0, most=False) -> float:
    """ Returns center_x aligned to """
    if most:
        new_left = min([shape.left for shape in shapes])
    else:
        new_left = shapes[index].left
    for shape in shapes:
        shape.left = new_left
    return new_left


def _align_top(shapes: List[Rectangle], index: int = 0, most=False) -> float:
    """ Returns bottom aligned to """
    if most:
        new_top = max([shape.top for shape in shapes])
    else:
        new_top = shapes[index].top
    for shape in shapes:
        shape.top = new_top
    return new_top


def _align_bottom(shapes: List[Rectangle], index: int = 0, most=False) -> float:
    """ Returns bottom aligned to """
    if most:
        new_bottom = min([shape.bottom for shape in shapes])
    else:
        new_bottom = shapes[index].bottom
    for shape in shapes:
        shape.bottom = new_bottom
    return new_bottom


def _stack_right(shapes: List[Rectangle], *, sep: float) -> (float, float):
    """ Returns last elem's position """
    self = None
    for i in range(len(shapes)):
        if i == 0:
            continue
        self = shapes[i]
        prev = shapes[i - 1]
        self.center_x = prev.center_x + round(prev.width / 2 + sep +
                                              self.width / 2, PRECISION)
    assert self is not None, 'For one key set it directly'
    return self.position


def _create_keys(symbols: List[int], width: float, height: float,
                 **kwargs) -> List[Key]:
    """  Specify specific width & height using kwargs """
    out = []
    posn = kwargs.pop('position', (0, 0))
    scaling = kwargs.pop('scaling', 1)
    kwargs = key.add_synonyms(kwargs)
    for symbol in symbols:
        key_name = key.symbol_string(symbol)
        if key_name in kwargs:
            size = kwargs[key_name]
            assert isinstance(size, tuple)
            out.append(Key(*posn, size[0] * scaling, size[1] * scaling, symbol, **kwargs))
        else:
            out.append(Key(*posn, width * scaling, height * scaling, symbol, **kwargs))
    return out


def _create_small_notebook_keys(verbose=False, **kwargs) -> Dict[int, Key]:
    color = kwargs.pop('key_color', arcade.color.BLACK)
    alpha = kwargs.pop('key_alpha', 255)
    size_normal = (1.125, 1.125)
    size_f = (1.075, 0.725)
    size_arrow_keys = (1.075, 0.525)

    key_plan = key.key_plan['small notebook']
    special_key_sizes = [{'SPACE': (6.525, 1.125)},
                         {'LSHIFT': (2.325, 1.125), 'RSHIFT': (2.775, 1.125)},
                         {'CAPSLOCK': (1.725, 1.125), 'ENTER': (2.175, 1.125)},
                         {'TAB': (1.425, 1.125), 'BACKSLASH': (1.275, 1.125)},
                         {'QUOTELEFT': (0.825, 1.125), 'BACKSPACE': (1.875, 1.125)},  # GRAVE -> QUOTELEFT
                         {}]
    arrow_keys = [[key.LEFT, key.DOWN, key.RIGHT],
                  [key.UP]]

    out = []  # type: List[List]
    # create keys in row 0
    temp = _create_keys(key_plan[0], *size_normal, **special_key_sizes[0],
                        scaling=SCALING, color=color, alpha=alpha)
    temp[0].left = 0
    temp[0].bottom = 0
    _stack_right(temp, sep=SEP * SCALING)
    _align_bottom(temp)
    out.append(temp)

    # create arrow keys
    temp = _create_keys(arrow_keys[0], *size_arrow_keys,
                        scaling=SCALING, color=color, alpha=alpha)
    temp[0].left = out[0][-1].right + SEP * SCALING
    temp[0].bottom = out[0][-1].bottom
    _stack_right(temp, sep=SEP * SCALING)
    _align_bottom(temp)
    out2 = temp  # type: List

    scaled_size = size_arrow_keys[0] * SCALING, size_arrow_keys[1] * SCALING
    temp = Key(temp[1].center_x, 0, *scaled_size, key.UP, color=color, alpha=alpha)
    temp.bottom = out2[1].top + SEP * SCALING
    out2.append(temp)

    # create keys in row 1-4
    for i in range(1, 5):
        temp = _create_keys(key_plan[i], *size_normal, **special_key_sizes[i],
                            scaling=SCALING, color=color, alpha=alpha)
        temp[0].left = 0
        temp[0].bottom = out[i - 1][0].top + SEP * SCALING
        _stack_right(temp, sep=SEP * SCALING)
        _align_bottom(temp)
        out.append(temp)

    # create F keys (row 5)
    temp = _create_keys(key_plan[5], *size_f,
                        scaling=SCALING, color=color, alpha=alpha)
    temp[0].left = 0
    temp[0].bottom = out[4][0].top + SEP * SCALING
    _stack_right(temp, sep=SEP * SCALING)
    _align_bottom(temp)
    out.append(temp)

    d = {}
    # remove after finish
    if verbose:
        for lst in out:
            for elem in lst:
                d[elem.symbol] = elem
                print(elem)
            print()
        for elem in out2:
            d[elem.symbol] = elem
            print(elem)
        return d

    for lst in out:
        for elem in lst:
            d[elem.symbol] = elem
    for elem in out2:
        d[elem.symbol] = elem
    return d


def _create_large_notebook_keys() -> Dict[int, Key]:
    raise NotImplementedError


def _create_mechanical_keys() -> Dict[int, Key]:
    # center_cluster = [PRINT, SCROLLLOCK, PAUSE,
    #                   INSERT, HOME, PAGEUP,
    #                   DELETE, END, PAGEDOWN]
    # arrow_keys = [LEFT, DOWN, RIGHT, UP]
    raise NotImplementedError


class Keyboard(Rectangle):
    def __init__(self, center_x, center_y, *, model: str, **kwargs):
        model = model
        assert model in ('small notebook', 'large notebook', 'mechanical')
        key_color = kwargs.pop('key_color', arcade.color.WHITE)
        key_alpha = kwargs.pop('key_alpha', 255)

        width, height, self.edge = {'small notebook': (18.05, 7.6, 0.4375),
                                    'large notebook': (22.85, 7.6, 0.4375),
                                    'mechanical': (23.4, 9.0, 0.6)}[model]
        super().__init__(center_x, center_y, width * SCALING, height * SCALING, **kwargs)
        self.keys = {'small notebook': _create_small_notebook_keys,
                     'large notebook': _create_large_notebook_keys,
                     'mechanical': _create_mechanical_keys}[model](key_color=key_color, key_alpha=key_alpha)

        lower_left_z_key = (self.left + self.edge * SCALING, self.bottom + self.edge * SCALING)
        for k in self.keys.values():
            k.move(*lower_left_z_key)

    def update(self):
        super().update()
        for k in self.keys.values():
            k.update()

    def draw(self):
        super().draw()
        for k in self.keys.values():
            k.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        # for testing
        try:
            self.keys[symbol].on_key_press(symbol, modifiers)
        except KeyError:
            pass
        if symbol == key.Q:
            self.keys[key.W].come_in(1, arcade.color.GREEN)

    def on_key_release(self, symbol: int, modifiers: int):
        self.keys[symbol].on_key_release(symbol, modifiers)

    def set_update_rate(self, rate: float):
        self.update_rate = rate
        for key in self.keys.values():
            key.set_update_rate(rate)
