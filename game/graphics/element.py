from typing import Optional

from .primitives import UIElement, DrawableRectangle, Group
from .text import Text


class Button(UIElement):
    """ Represents a button drawn using arcade.Shape """
    def __init__(self,
                 center_x: float, center_y: float,
                 width: float, height: float,
                 color: (int, int, int), alpha: int = 255,
                 **kwargs):
        rec = DrawableRectangle(center_x, center_y, width, height, color, alpha)
        self.color = self.drawable.color
        self.pressed_color = kwargs.pop('pressed_color', None)  # type: Optional[(int, int, int)]
        self.text = kwargs.pop('text', None)  # type: Optional[Text]
        drawable = Group([rec, self.text], name='Button')
        super().__init__(drawable=drawable)

    def on_press(self):
        if self.pressed_color:
            self.drawable.color = self.pressed_color
        else:
            self.drawable.color = self.color[0]-20, self.color[0]-20, self.color[0]-20

    def on_release(self):
        self.drawable.color = self.color

    def on_focus(self):
        pass

    def on_hover(self):
        pass

    def on_out(self):
        pass









