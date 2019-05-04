from __future__ import annotations

from functools import partial

from pyglet import gl

glClear = partial(gl.glClear, gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


class GraphicsEngine:
    """ Manages graphical effects and background/video """

    __slots__ = '_pointer', '_elements', '_layers'

    def __init__(self):

    def update(self):
        """ Update graphics to match current data """
        pass

    def force_update(self):
        pass

    def on_draw(self):
        """ Draws everything on the screen """
        glClear()

        self._draw_pointer()

    def _draw_pointer(self):
        """ Draw custom pointer """
        pass

    # def _draw_fps(self):
    #     """ Show FPS on screen """
    #     fps = _time_engine.fps
    #     output = f"FPS: {fps:.1f}"
    #     arcade.draw_text(output, 20, _window.height // 2, arcade.color.WHITE, 16)
