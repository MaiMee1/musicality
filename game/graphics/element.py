from typing import Optional, Tuple

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

        self.action = {
            'on_press': lambda *args: None,
            'on_release': lambda *args: None,
            'on_focus': lambda *args: None,
            'on_hover': lambda *args: None,
            'on_out': lambda *args: None,
            'on_draw': lambda *args: None,
        }

    def draw(self):
        self.action['on_draw'](self)
        super().draw()

    def on_press(self):
        """ Changes color to darker """
        a = self.action['on_press'](self)
        if a is None:
            if self.secondary_color:
                self.rectangle.color = self.secondary_color
            else:
                self.rectangle.color = self.primary_color[0] * .7, self.primary_color[1] * .7, self.primary_color[2] * .7

    def on_release(self):
        a = self.action['on_release'](self)
        if a is None:
            self.rectangle.color = self.primary_color

    def on_focus(self):
        self.action['on_focus'](self)

    def on_hover(self):
        self.action['on_hover'](self)

    def on_out(self):
        self.action['on_out'](self)

    @property
    def text(self) -> Optional[Text]:
        return self._text

    @text.setter
    def text(self, new_value: Text):
        if self._text:
            self.drawable.remove(self._text)
        self._text = new_value
        self.drawable.append(self._text)







