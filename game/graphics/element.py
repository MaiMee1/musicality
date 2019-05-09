from __future__ import annotations

from typing import Optional, Tuple, Dict, Callable, Union, List, Any

from game.graphics.primitives import Drawable, Movable, DrawableRectangle, Group, Shape
from game.graphics.texture import Sprite
from game.graphics.text import Text


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

        self.pressed = False
        self.in_ = False

        self._action = {
            'on_press': [],
            'on_release': [],
            'on_focus': [],
            'on_hover': [],
            'on_in': [],
            'on_out': [],
            'on_draw': [],
        }  # type: Dict[str:List[Tuple[Callable[['UIElement'], Any], Any]]]

    def _call_action(self, key: str):
        """ Call all actions with `key` with unique `id_`.
        Remove any actions that have timeout-ed. """
        cache = set()
        if self._action[key]:
            for index, (action, id_) in enumerate(self._action[key]):
                if id_ not in cache:
                    try:
                        action(self)
                        cache.add(id_)
                        # uses set to make it faster (hopefully)
                    except TimeoutError:
                        # print(f"action {action} timeout, removed"
                        self._action[key].pop(index)

    def add_action(self, key: str, action: Callable[[__class__], Any], id_: Optional[Any] = None):
        """ Add an action to stack with `key` and optionally `id_` """
        if id_ is None:
            id_ = id(action)
        if id_ in (elem for _, elem in self._action[key]):
            # already has id
            pass
        else:
            self._action[key].append((action, id_))

    def remove_action(self, key: str, id_: Optional[Any] = None, action: Optional[Callable[[__class__], Any]] = None):
        """ Remove an action to stack with `key` and `id_` """
        if id_ is None:
            raise NotImplementedError
        for index, (_, elem) in enumerate(self._action[key]):
            if elem == id_:
                self._action[key].pop(index)
                # only remove one
                break

    def draw(self):
        """ Draw the element """
        self._call_action('on_draw')
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

    def on_hover(self):
        self._call_action('on_hover')

    def on_focus(self):
        self._call_action('on_focus')

    def on_in(self):
        self._call_action('on_in')
        self.in_ = True

    def on_out(self):
        self._call_action('on_out')
        self.in_ = False

    def on_press(self):
        self._call_action('on_press')
        self.pressed = True

    def on_release(self):
        self._call_action('on_release')
        self.pressed = False


class Button(UIElement):
    """ Represents a button drawn using arcade.Shape """
    def __init__(self,
                 center_x: float, center_y: float,
                 width: float, height: float,
                 color: Tuple[int, int, int], alpha: int = 255,
                 **kwargs):

        self.rectangle = DrawableRectangle(center_x, center_y, width, height, color, alpha)
        self.primary_color = self.rectangle.color
        self.secondary_color = kwargs.pop('secondary_color', None)  # type: Optional[(int, int, int)]

        self._text = kwargs.pop('text', None)  # type: Optional[Text]
        drawable = Group([self.rectangle], name='Button')
        if self._text:
            drawable.append(self._text)

        super().__init__(drawable=drawable)

        # self._action['on_press'] = [(self.default_color_change, id('default_color_change'))]
        # self._action['on_release'] = [(partial(setattr, (self, 'rectangle', self.primary_color)), id('on_release'))]

    def default_color_change(self):
        if self.secondary_color:
            self.rectangle.color = self.secondary_color
        else:
            self.rectangle.color = self.primary_color[0] * .7, self.primary_color[1] * .7, self.primary_color[2] * .7

    @property
    def text(self) -> Optional[Text]:
        return self._text

    @text.setter
    def text(self, new_value: Text):
        if self._text:
            self.drawable.remove(self._text)
        self._text = new_value
        self.drawable.append(self._text)


class DropDown(UIElement):
    pass


class Slider(UIElement):
    pass

