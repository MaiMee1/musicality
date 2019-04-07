"""
Due to limitations of the library (I think), the FN key does not work.
RSHIFT also registers as LSHIFT in many computer's keyboard.

"""
from typing import Dict, List

import arcade
from arcade.arcade_types import Color, RGBA

import key
from song import HitObject

SCALING_CONSTANT = 1
SEP = 0.075
SCALING = SCALING_CONSTANT / SEP
PRECISION = 10


def set_scaling(new_value):
    global SCALING_CONSTANT, SCALING
    SCALING_CONSTANT = new_value
    SCALING = SCALING_CONSTANT / SEP


class Rectangle:
    def __init__(self, center_x: float, center_y: float, width: float, height: float,
                 color: Color = arcade.color.BLACK, alpha: int = 255, **kwargs):

        self.width = width
        self.height = height
        self._position = [center_x, center_y]

        # self.color = kwargs.pop('color', arcade.color.BLACK)  # type: Color
        # self.alpha = kwargs.pop('alpha', 255)  # type: int
        self.border_width = kwargs.pop('border_width', 1)  # type: float
        self.tilt_angle = kwargs.pop('tilt_angle', 0)  # type: float
        self.filled = kwargs.pop('filled', True)  # type: float

        self.color = color
        self.alpha = alpha

        # self.border_width = border_width
        # self.tilt_angle = tilt_angle
        # self.filled = filled

        self.shape = arcade.create_rectangle(
            self.center_x, self.center_y, self.width, self.height, self.rgba,
            border_width=self.border_width, tilt_angle=self.tilt_angle, filled=self.filled)
        self.redraw()

        # FIXME must set update rate overhere as well
        self._update_rate = 1/60.5

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
    def rgba(self) -> Color:
        return self.color[0], self.color[1], self.color[2], self.alpha

    @property
    def size(self) -> (float, float):
        return self.width, self.height

    def update(self):
        """ Advance by one frame """
        # Does not check when to redraw for performance reasons
        pass

    def draw(self):
        """ Draw VBO """
        self.shape.draw()

    def redraw(self):
        """ Recreate VBO """
        self.shape = arcade.create_rectangle(
            self.center_x, self.center_y, self.width, self.height, self.rgba,
            border_width=self.border_width, tilt_angle=self.tilt_angle, filled=self.filled)

    @property
    def update_rate(self):
        return self._update_rate

    @update_rate.setter
    def update_rate(self, rate: float):
        self._update_rate = rate


class Key(Rectangle):

    COLOR_INACTIVE = arcade.color.BLACK, 150
    COLOR_PRESSED = arcade.color.WHITE, 255

    STATE_INACTIVE = 0
    STATE_ACTIVE = 1

    def __init__(self, center_x: float, center_y: float, width: float,
                 height: float, symbol: int, **kwargs):

        self.symbol = symbol
        self._stack = []  # type: List[arcade.Shape]
        self.to_draw = []  # type: List[arcade.Shape]
        self.state = [Key.STATE_INACTIVE]
        self.pressable = kwargs.pop('pressable', True)

        super().__init__(center_x, center_y, width, height, **kwargs)
        # self.color, self.alpha = Key.COLOR_INACTIVE
        # self.redraw()

    def __str__(self):
        return f"key constant: {self.symbol} size: {self.size} posn: {self._position}"

    def on_key_press(self, symbol: int, modifiers: int):
        assert symbol == self.symbol
        if self.pressable:
            self.color, self.alpha = Key.COLOR_PRESSED
            self.redraw()

    def on_key_release(self, symbol: int, modifiers: int):
        assert symbol == self.symbol
        if self.pressable:
            self.color, self.alpha = Key.COLOR_INACTIVE
            self.redraw()

    def setup_stack(self, delta_time: float, rgba: RGBA):
        # FIXME generator create at 'compile' time
        # TODO let update_rate get from runtime
        # create a generator
        self._stack = (
            arcade.create_rectangle(
                self.center_x, self.center_y,
                1 + (self.width - 1) * self.update_rate * i / delta_time,
                1 + (self.height - 1) * self.update_rate * i / delta_time,
                rgba, tilt_angle=self.tilt_angle)
            for i in range(1, int(delta_time / self.update_rate) + 1)
        )

    def update(self):
        """ Advance by one frame getting to_draw from stack """
        try:
            if self._stack:
                self.to_draw.append(next(self._stack))
        except StopIteration:
            self._stack = None

    # def come_in(self, delta_clock: float, rgba: RGBA):
    #     # create a list
    #     self._stack = [
    #         arcade.create_rectangle(
    #             self.center_x, self.center_y,
    #             1 + (self.width - 1) * self.update_rate * i / delta_clock,
    #             1 + (self.height - 1) * self.update_rate * i / delta_clock,
    #             rgba, tilt_angle=self.tilt_angle)
    #         for i in range(1, int(delta_clock / self.update_rate) + 1)
    #     ]
    #
    # def update(self):
    #     """ Advance by one frame getting to_draw from stack """
    #     try:
    #         if self._stack:
    #             self.to_draw.append(self._stack.pop(0))
    #     except StopIteration:
    #         self._stack = None

    def draw(self):
        """ Draw self and things in to_draw """
        self.shape.draw()
        if self.to_draw:
            for shape in self.to_draw:
                shape.draw()
            self.to_draw = []


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
        self.center_x = prev.center_x + round(prev.width/2 + sep + self.width/2, PRECISION)
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
            out.append(Key(*posn, size[0]*scaling, size[1] * scaling, symbol, **kwargs))
        else:
            out.append(Key(*posn, width*scaling, height * scaling, symbol, **kwargs))
    return out


def _create_small_notebook_keys(verbose=False, **kwargs) -> Dict[int, Key]:
    color = kwargs.pop('key_color', Key.COLOR_INACTIVE[0])
    alpha = kwargs.pop('key_alpha', Key.COLOR_INACTIVE[1])
    size_normal = (1.125, 1.125)
    size_f = (1.075, 0.725)
    size_arrow_keys = (1.075, 0.525)

    key_plan = key.key_plan['small notebook']
    special_key_sizes = key.key_specs['small notebook']
    arrow_keys = [[key.LEFT, key.DOWN, key.RIGHT],
                  [key.UP]]

    out = []  # type: List[List]
    # create keys in row 0
    temp = _create_keys(key_plan[0], *size_normal, **special_key_sizes[0],
                        scaling=SCALING, color=color, alpha=alpha)
    temp[0].left = 0
    temp[0].bottom = 0
    _stack_right(temp, sep=SEP*SCALING)
    _align_bottom(temp)
    out.append(temp)

    # create arrow keys
    temp = _create_keys(arrow_keys[0], *size_arrow_keys,
                        scaling=SCALING, color=color, alpha=alpha)
    temp[0].left = out[0][-1].right + SEP*SCALING
    temp[0].bottom = out[0][-1].bottom
    _stack_right(temp, sep=SEP*SCALING)
    _align_bottom(temp)
    out2 = temp  # type: List

    scaled_size = size_arrow_keys[0] * SCALING, size_arrow_keys[1] * SCALING
    temp = Key(temp[1].center_x, 0, *scaled_size, key.UP, color=color, alpha=alpha)
    temp.bottom = out2[1].top + SEP*SCALING
    out2.append(temp)

    # create keys in row 1-4
    for i in range(1, 5):
        temp = _create_keys(key_plan[i], *size_normal, **special_key_sizes[i],
                            scaling=SCALING, color=color, alpha=alpha)
        temp[0].left = 0
        temp[0].bottom = out[i - 1][0].top + SEP*SCALING
        _stack_right(temp, sep=SEP*SCALING)
        _align_bottom(temp)
        out.append(temp)

    # create F keys (row 5)
    temp = _create_keys(key_plan[5], *size_f,
                        scaling=SCALING, color=color, alpha=alpha)
    temp[0].left = 0
    temp[0].bottom = out[4][0].top + SEP * SCALING
    _stack_right(temp, sep=SEP*SCALING)
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

        self.keys = {
            'small notebook': _create_small_notebook_keys,
            'large notebook': _create_large_notebook_keys,
            'mechanical': _create_mechanical_keys
        }[model]()

        width, height, self.edge = {'small notebook': (18.05, 7.6, 0.4375),
                                    'large notebook': (22.85, 7.6, 0.4375),
                                    'mechanical': (23.4, 9.0, 0.6)}[model]
        super().__init__(center_x, center_y, width * SCALING, height * SCALING, **kwargs)

        lower_left_z_key = self.left + self.edge*SCALING, self.bottom + self.edge*SCALING
        for k in self.keys.values():
            k.move(*lower_left_z_key)

    def update(self):
        """ Advance self and its keys by one frame """
        for k in self.keys.values():
            k.update()

    def draw(self):
        """ Draw self and its keys """
        super().draw()
        for k in self.keys.values():
            k.draw()

    def redraw(self):
        """ Recreate self's and optionally all keys' VBO """
        super().redraw()
        for k in self.keys.values():
            k.redraw()

    def on_key_press(self, symbol: int, modifiers: int):
        try:
            self.keys[symbol].on_key_press(symbol, modifiers)
        except KeyError:
            # do nothing if key does not exist on keyboard
            pass
        # for testing
        if symbol == key.ESCAPE:
            self.keys[key.F1].setup_stack(1, arcade.color.GREEN)
        if symbol == key.F12:
            for k in self.keys.values():
                k.setup_stack(1, arcade.color.GREEN)

    def on_key_release(self, symbol: int, modifiers: int):
        try:
            self.keys[symbol].on_key_release(symbol, modifiers)
        except KeyError:
            # do nothing if key does not exist on keyboard
            pass

    def set_update_rate(self, rate: float):
        self.update_rate = rate
        for k in self.keys.values():
            k.update_rate = rate

    def send(self, hit_object: HitObject):
        k = self.keys[hit_object.symbol]
        k.setup_stack(hit_object.reach_time - hit_object.start_time, arcade.color.PINK)
        k.state = Key.STATE_ACTIVE
