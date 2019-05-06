from typing import Optional, Tuple, Dict, Callable

from game.graphics.primitives import UIElement, DrawableRectangle, Group
from game.graphics.text import Text


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

    def draw(self):
        if self.action['on_draw']:
            self.action['on_draw'](self)
        super().draw()

    def on_press(self):
        """ Calls action:on_press default behaviour changes color to darker """
        if self.action['on_press']:
            self.action['on_press'](self)
        else:
            if self.secondary_color:
                self.rectangle.color = self.secondary_color
            else:
                self.rectangle.color = self.primary_color[0] * .7, self.primary_color[1] * .7, self.primary_color[2] * .7
            self.pressed = True

    def on_release(self):
        if self.action['on_release']:
            self.action['on_release']()
        else:
            self.rectangle.color = self.primary_color
            self.pressed = False

    @property
    def text(self) -> Optional[Text]:
        return self._text

    @text.setter
    def text(self, new_value: Text):
        if self._text:
            self.drawable.remove(self._text)
        self._text = new_value
        self.drawable.append(self._text)

