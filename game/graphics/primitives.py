from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Iterable, Union, Optional, Dict

import arcade

from game.constants import MouseState, MOUSE_STATE


class Drawable(metaclass=ABCMeta):
    """ Base class for graphical objects """

    @abstractmethod
    def draw(self):
        """ Draw the graphical element """
        pass


class Layer(Drawable):

    number = 0
    last_z = 0

    __slots__ = 'visible', 'elements', 'name', 'z'

    def __init__(self, elements: Iterable[Drawable], **kwargs):
        self.visible = True
        self.elements = list(elements)
        name = kwargs.pop('name', 'Layer')
        self.name = f'{name} {Layer.number}'
        Layer.number += 1
        self.z = kwargs.pop('z', Layer.last_z + 1)
        Layer.last_z = self.z

    def __str__(self):
        if self.name:
            return self.name

    def draw(self):
        """ Draw all elements in self """
        if self.visible:
            try:
                for elem in self.elements:
                    elem.draw()
            except AttributeError as e:
                e.args = (f'{elem} is not drawable',)
                raise

    def __iter__(self):
        return self.elements

    def remove(self, element: Drawable):
        self.elements.remove(element)

    def pop(self, index: int) -> Drawable:
        return self.elements.pop(index)


class Movable(metaclass=ABCMeta):

    @abstractmethod
    def move(self, delta_x: float, delta_y: float):
        """ Move the object ny `delta_x` and `delta_y`"""
        pass


class Group(Drawable, Movable):

    number = 0

    __slots__ = 'visible', 'elements', 'name', '_anchor', '_ref_index'

    def __init__(self, elements: Iterable, **kwargs):
        self.visible = True
        assert elements
        self.elements = list(elements)
        name = kwargs.pop('name', f'Group')
        self.name = f'{name} {Group.number}'
        Group.number += 1
        self._anchor = kwargs.pop('anchor', self.elements[0].position)
        self._ref_index = kwargs.pop('ref', 0)  # type: int

    def __str__(self):
        if self.name:
            return self.name

    def draw(self):
        """ Draw all elements in self """
        if self.visible:
            for elem in self.elements:
                try:
                    elem.draw()
                except AttributeError as e:
                    e.args = (f'{elem} is not drawable',)
                    raise

    def move(self, delta_x: float, delta_y: float):
        """ Move the group by `delta_x` and `delta_y`"""
        for elem in self.elements:
            try:
                elem.move(delta_x, delta_y)
            except AttributeError as e:
                e.args = (f'{elem} is not movable',)
                raise

    def is_inside(self, x: float, y: float):
        for elem in self.elements:
            try:
                if elem.is_inside(x, y):
                    return True
            except AttributeError:
                pass
        return False

    @property
    def anchor(self) -> (float, float):
        return self._anchor

    @anchor.setter
    def anchor(self, new_value: (float, float)):
        """ Change anchor without moving """
        self._ref_index = None
        self._anchor = [new_value[0], new_value[1]]

    @property
    def position(self) -> (float, float):
        if self._ref_index is not None:
            return self.elements[self._ref_index].position
        return self._anchor

    @position.setter
    def position(self, new_value: (float, float)):
        if self._ref_index is not None:
            dx, dy = new_value[0]-self.position[0], new_value[1]-self.position[1]
        else:
            dx, dy = new_value[0]-self._anchor[0], new_value[1]-self._anchor[1]
            self._anchor = new_value
        self.move(dx, dy)

    @property
    def top(self):
        if self._ref_index is not None:
            return self.elements[self._ref_index].top

    @top.setter
    def top(self, new_value: float):
        if not self.top:
            raise AttributeError("can't set attribute")
        dy = new_value-self.top
        self.move(0, dy)

    @property
    def bottom(self):
        if self._ref_index is not None:
            return self.elements[self._ref_index].bottom

    @bottom.setter
    def bottom(self, new_value: float):
        if not self.bottom:
            raise AttributeError("can't set attribute")
        dy = new_value-self.bottom
        self.move(0, dy)

    @property
    def left(self):
        if self._ref_index is not None:
            return self.elements[self._ref_index].left

    @left.setter
    def left(self, new_value: float):
        if not self.left:
            raise AttributeError("can't set attribute")
        dx = new_value-self.left
        self.move(dx, 0)

    @property
    def right(self):
        if self._ref_index is not None:
            return self.elements[self._ref_index].right

    @right.setter
    def right(self, new_value: float):
        if not self.right:
            raise AttributeError("can't set attribute")
        dx = new_value-self.right
        self.move(dx, 0)

    def __iter__(self):
        return self.elements

    def append(self, element: Union[Drawable, Movable]):
        self.elements.append(element)

    def remove(self, element: Union[Drawable, Movable]):
        self.elements.remove(element)

    def pop(self, index: int) -> Union[Drawable, Movable]:
        return self.elements.pop(index)

    @property
    def ref(self) -> Optional[Union[Drawable, Movable]]:
        if self._ref_index:
            return self.elements[self._ref_index]

    def set_ref(self, index: int = None, element=None):
        if index:
            self._ref_index = index
        elif element:
            index = self.elements.index(element)
            self._ref_index = index

    def __getitem__(self, item):
        return self.elements[item]

    def __setitem__(self, key, value):
        self.elements[key] = value


class Shape(Movable):

    PRECISION = 10

    __slots__ = '_position'

    def __init__(self, center_x: float, center_y: float):
        self._position = [center_x, center_y]

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

    def move(self, delta_x: float, delta_y: float):
        self.center_x += delta_x
        self.center_y += delta_y

    @abstractmethod
    def is_inside(self, x: float, y: float) -> bool:
        """ Return True if point (x, y) is inside, False otherwise. """
        pass

    @property
    @abstractmethod
    def top(self):
        pass

    @top.setter
    @abstractmethod
    def top(self, new_value: float):
        pass

    @property
    @abstractmethod
    def bottom(self):
        pass

    @bottom.setter
    @abstractmethod
    def bottom(self, new_value: float):
        pass

    @property
    @abstractmethod
    def left(self):
        pass

    @left.setter
    @abstractmethod
    def left(self, new_value: float):
        pass

    @property
    @abstractmethod
    def right(self):
        pass

    @right.setter
    @abstractmethod
    def right(self, new_value: float):
        pass


class Rectangle(Shape):

    __slots__ = 'width', 'height', '_position'

    def __init__(self, center_x: float, center_y: float, width: float, height: float):
        super().__init__(center_x, center_y)
        self.width = width
        self.height = height

    def _get_right(self) -> float:
        return self._position[0] + round(self.width / 2, self.PRECISION)

    def _set_right(self, new_value: float):
        self.center_x += new_value - round(self.width / 2, self.PRECISION) - self.center_x

    right = property(_get_right, _set_right)

    def _get_left(self) -> float:
        return self._position[0] - round(self.width / 2, self.PRECISION)

    def _set_left(self, new_value: float):
        self.center_x += new_value + round(self.width / 2, self.PRECISION) - self.center_x

    left = property(_get_left, _set_left)

    def _get_top(self) -> float:
        return self._position[1] + round(self.height / 2, self.PRECISION)

    def _set_top(self, new_value: float):
        self.center_y += new_value - round(self.height / 2, self.PRECISION) - self.center_y

    top = property(_get_top, _set_top)

    def _get_bottom(self) -> float:
        return self._position[1] - round(self.height / 2, self.PRECISION)

    def _set_bottom(self, new_value: float):
        self.center_y += new_value + round(self.height / 2, self.PRECISION) - self.center_y

    bottom = property(_get_bottom, _set_bottom)

    @property
    def size(self) -> (float, float):
        return self.width, self.height

    def is_inside(self, x: float, y: float) -> bool:
        """ Return True if point (x, y) is inside, False otherwise """
        return self.left <= x <= self.right and self.bottom <= y <= self.top


class Circle(Shape):

    __slots__ = '_position', 'radius'

    def __init__(self, center_x: float, center_y: float, radius: float):
        super().__init__(center_x, center_y)
        self.radius = radius

    def _get_right(self) -> float:
        return self._position[0] + self.radius

    def _set_right(self, new_value: float):
        self.center_x += new_value - self.radius - self.center_x

    right = property(_get_right, _set_right)

    def _get_left(self) -> float:
        return self._position[0] - self.radius

    def _set_left(self, new_value: float):
        self.center_x += new_value + self.radius - self.center_x

    left = property(_get_left, _set_left)

    def _get_top(self) -> float:
        return self._position[1] + self.radius

    def _set_top(self, new_value: float):
        self.center_y += new_value - self.radius - self.center_y

    top = property(_get_top, _set_top)

    def _get_bottom(self) -> float:
        return self._position[1] - self.radius

    def _set_bottom(self, new_value: float):
        self.center_y += new_value + self.radius - self.center_y

    bottom = property(_get_bottom, _set_bottom)

    def is_inside(self, x: float, y: float) -> bool:
        """ Return True if point (x, y) is inside, False otherwise """
        return ((self.center_x - x)**2 + (self.center_y - y)**2)*0.5 < self.radius


class DrawableRectangle(Rectangle, Drawable):

    def __init__(self,
                 center_x: float, center_y: float,
                 width: float, height: float,
                 color: arcade.Color = arcade.color.WHITE, alpha: int = 255,
                 **kwargs):
        super().__init__(center_x, center_y, width, height)
        self.visible = True
        self._border_width = kwargs.pop('border_width', 1)  # type: float
        self._tilt_angle = kwargs.pop('tilt_angle', 0)  # type: float
        self._filled = kwargs.pop('filled', True)  # type: float

        self._color = color
        self._alpha = alpha

        self._shape = None
        self.change_resolved = False
        self.recreate_vbo()

    def __str__(self):
        return f"size: {self.size} posn: {self._position}"

    def _get_opacity(self) -> float:
        return round(self._alpha / 255, 1)

    def _set_opacity(self, new_value: float):
        self._alpha = int(round(new_value * 255, 0))

    opacity = property(_get_opacity, _set_opacity)

    @property
    def color(self) -> (int, int, int):
        return self._color

    @color.setter
    def color(self, new_value: (int, int, int)):
        r, g, b = new_value
        try:
            assert isinstance(r, int)
            assert isinstance(g, int)
            assert isinstance(b, int)
        except AssertionError as e:
            try:
                new_value = int(r), int(g), int(b)
            except TypeError as e:
                e.args = ('color must be in rgb format with int values',)
                raise
        self._color = new_value
        self.change_resolved = False

    @property
    def alpha(self) -> int:
        return self._alpha

    @alpha.setter
    def alpha(self, new_value: int):
        assert isinstance(new_value, int)
        assert 0 <= new_value <= 255
        self._alpha = new_value
        self.change_resolved = False

    @property
    def rgba(self) -> (int, int, int, int):
        return self.color[0], self.color[1], self.color[2], self._alpha

    def draw(self):
        if self.visible:
            if not self.change_resolved:
                self.recreate_vbo()
            self._shape.draw()

    def move(self, delta_x: float, delta_y: float):
        self.center_x += delta_x
        self.center_y += delta_y
        self.change_resolved = False

    def recreate_vbo(self):
        self._shape = arcade.create_rectangle(
            self.center_x, self.center_y, self.width, self.height, self.rgba,
            self._border_width, self._tilt_angle, self._filled
        )
        self.change_resolved = True


class Sprite(arcade.Sprite, Drawable, Movable):

    point_sprite = arcade.Sprite()
    point_sprite.points = (0, 0)

    def is_inside(self, x: float, y: float):
        Sprite.point_sprite.points = (x, y)
        return arcade.check_for_collision(self, Sprite.point_sprite)

    def move(self, delta_x: float, delta_y: float):
        self.center_x += delta_x
        self.center_y += delta_y


class UIElement(Drawable, Movable):
    """ Represents a UI element """

    def __init__(self,
                 drawable: Union[Group, Drawable, Sprite],
                 ref_shape: Shape = None):
        self.visible = True
        self.drawable = drawable  # Preferably Group and movable too
        self.ref_shape = ref_shape
        if ref_shape is None:
            assert hasattr(self.drawable, 'is_inside')
        self._custom_mouse = None  # type: Optional[Dict[MouseState, Sprite]]
        self.pressed = False
        self.in_ = False

    def draw(self):
        """ Draw the element """
        if self.visible:
            self.drawable.draw()

    def move(self, delta_x: float, delta_y: float):
        """ Move element by `delta_x` and `delta_y` """
        self.drawable.move(delta_x, delta_y)
        if self.ref_shape:
            self.ref_shape.move(delta_x, delta_y)

    @property
    def position(self) -> (float, float):
        """ Return the center_x and center_y of the element """
        if self.ref_shape:
            return self.ref_shape.position
        return self.drawable.position

    @position.setter
    def position(self, new_value: (float, float)):
        """ Set center of the element to `new_value` """
        if self.ref_shape:
            self.ref_shape.position = new_value
        self.drawable.position = new_value

    @property
    def right(self):
        if self.ref_shape:
            return self.ref_shape.right
        return self.drawable.right

    @right.setter
    def right(self, new_value: float):
        if not self.ref_shape:
            self.drawable.right = new_value
            return
        dx = new_value - self.right
        self.ref_shape.right = new_value
        try:
            self.drawable.right = new_value
        except AttributeError:
            self.drawable.move(dx, 0)

    @property
    def left(self):
        if self.ref_shape:
            return self.ref_shape.left
        return self.drawable.left

    @left.setter
    def left(self, new_value: float):
        if not self.ref_shape:
            self.drawable.left = new_value
            return
        dx = new_value - self.left
        self.ref_shape.left = new_value
        try:
            self.drawable.left = new_value
        except AttributeError:
            self.drawable.move(dx, 0)

    @property
    def top(self):
        if self.ref_shape:
            return self.ref_shape.top
        return self.drawable.top

    @top.setter
    def top(self, new_value: float):
        if not self.ref_shape:
            self.drawable.top = new_value
            return
        dy = new_value - self.top
        self.ref_shape.top = new_value
        try:
            self.drawable.top = new_value
        except AttributeError:
            self.drawable.move(0, dy)

    @property
    def bottom(self):
        if self.ref_shape:
            print('ref_shape')
            return self.ref_shape.bottom
        return self.drawable.bottom

    @bottom.setter
    def bottom(self, new_value: float):
        if not self.ref_shape:
            self.drawable.bottom = new_value
            return
        dy = new_value - self.bottom
        self.ref_shape.bottom = new_value
        try:
            self.drawable.bottom = new_value
        except AttributeError:
            self.drawable.move(0, dy)

    def is_inside(self, x: float, y: float):
        if self.ref_shape:
            return self.ref_shape.is_inside(x, y)
        return self.drawable.is_inside(x, y)

    def get_mouse_sprite(self, mouse_state: MouseState) -> Optional[Sprite]:
        assert mouse_state in MOUSE_STATE
        if self._custom_mouse:
            return self._custom_mouse[mouse_state]
        return None

    @abstractmethod
    def on_hover(self):
        pass

    @abstractmethod
    def on_focus(self):
        pass

    @abstractmethod
    def on_in(self):
        pass

    @abstractmethod
    def on_out(self):
        pass

    @abstractmethod
    def on_press(self):
        self.pressed = True
        pass

    @abstractmethod
    def on_release(self):
        self.pressed = False
        pass
