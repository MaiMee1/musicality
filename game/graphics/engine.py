from __future__ import annotations

from functools import partial
from typing import List

from pyglet import gl

glClear = partial(gl.glClear, gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


class GraphicsEngine:
    """ Manages graphical effects and background/video """

    __slots__ = '_pointer', '_layers'

    def __init__(self):
        self._layers = []  # type: List[Layer]

    def update(self):
        """ Update graphics to match current data """
        pass

    def force_update(self):
        """ Force all VBOs to be redrawn """
        pass

    def on_draw(self):
        """ Draws everything on the screen """
        glClear()

        for layer in self._layers:
            layer.draw()

        self._draw_pointer()

    def _draw_pointer(self):
        """ Draw custom pointer """
        if self._pointer:
            self._pointer.draw()

    @property
    def bg(self):
        return self._layers[0]
