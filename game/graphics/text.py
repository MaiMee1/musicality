from __future__ import annotations

from typing import Tuple

from arcade import draw_text

from game.graphics.primitives import Drawable, Movable


class Text(Drawable, Movable):

    __slots__ = 'visible', 'text', '_position', '_color', 'size', '_font', '_angle'

    def __init__(self,
                 text: str,
                 x: float, y: float,
                 color: (int, int, int, int),
                 size: float,
                 font: Tuple[str] = ('calibri', 'arial'), **kwargs):
        """ Save value for text """
        self.visible = True
        self.text = text
        self._position = [x, y]
        self._color = color
        self.size = size
        self._font = font
        self._kwargs = kwargs

    def draw(self):
        """ Draw the text """
        if self.visible:
            draw_text(self.text, self.left, self.bottom, self._color,
                      self.size, font_name=self._font, **self._kwargs)

    @property
    def position(self) -> (float, float):
        return self._position[0], self._position[1]

    @position.setter
    def position(self, new_value: (float, float)):
        assert len(new_value) == 2
        self._position = list(new_value)

    @property
    def anchor_x(self) -> float:
        return self._position[0]

    @anchor_x.setter
    def anchor_x(self, new_value: float):
        self._position[0] = new_value

    @property
    def anchor_y(self) -> float:
        return self._position[1]

    @anchor_y.setter
    def anchor_y(self, new_value: float):
        self._position[1] = new_value

    # TODO make real center_x and center_y, alias for now
    center_x, center_y = anchor_x, anchor_y

    def move(self, delta_x: float, delta_y: float):
        self.anchor_x += delta_x
        self.anchor_y += delta_y

    @property
    def left(self) -> float:
        return self._position[0]

    @left.setter
    def left(self, new_value: float):
        self.anchor_x += new_value

    @property
    def top(self) -> float:
        return self._position[1]

    @top.setter
    def top(self, new_value: float):
        self.anchor_y += new_value

    @property
    def bottom(self) -> float:
        return self._position[1]

    @bottom.setter
    def bottom(self, new_value: float):
        self.anchor_y += new_value
