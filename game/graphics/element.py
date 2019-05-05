from typing import Optional, Tuple

from .primitives import UIElement, DrawableRectangle, Group
from .text import Text


class Button(UIElement):
    """ Represents a button drawn using arcade.Shape """
    def __init__(self,
                 center_x: float, center_y: float,
                 width: float, height: float,
                 color: Tuple[int, int, int], alpha: int = 255,
                 **kwargs):
        self.rec = DrawableRectangle(center_x, center_y, width, height, color, alpha)
        self.color = self.rec.color
        self.pressed_color = kwargs.pop('pressed_color', None)  # type: Optional[(int, int, int)]
        self._text = kwargs.pop('text', None)  # type: Optional[Text]
        drawable = Group([self.rec], name='Button')
        if self._text:
            drawable.append(self._text)
        super().__init__(drawable=drawable, ref_shape=self.rec)

    def on_press(self):
        """ Changes color to darker """
        if self.pressed_color:
            self.rec.color = self.pressed_color
        else:
            self.rec.color = self.color[0]*.8, self.color[0]*.8, self.color[0]*.8

    def on_release(self):
        self.rec.color = self.color

    def on_focus(self):
        pass

    def on_hover(self):
        pass

    def on_out(self):
        pass

    @property
    def text(self) -> Optional[Text]:
        return self._text

    @text.setter
    def text(self, new_value: Text):
        if self._text:
            self.drawable.remove(self._text)
        self._text = new_value
        self.drawable.append(self._text)









