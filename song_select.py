from __future__ import annotations

from pathlib import Path
from io import StringIO
from typing import Any, Union, Optional, Tuple, List, Dict, NewType, TextIO, Iterable, Callable, Hashable
import warnings
from random import random

import arcade
import pyglet


from constants import MouseState, MOUSE_STATE, UIElementState, UI_ELEMENT_STATE, GAME_STATE

_window = None  # type: Optional[arcade.Window]

_time_engine = None  # type: Optional[TimeEngine]
_audio_engine = None  # type: Optional[AudioEngine]
_graphics_engine = None  # type: Optional[GraphicsEngine]

_score_manager = None  # type: Optional[ScoreManager]
_hit_object_manager = None  # type: Optional[HitObjectManager]
_UI_manager = None  # type: Optional[UIManger]


class BaseShape:

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

    def move(self, delta_x: float, delta_y: float) -> (float, float):
        """ Return: new position """
        self.center_x += delta_x
        self.center_y += delta_y
        return self.position

    def is_inside(self, x: float, y: float) -> bool:
        """ Return True if point (x, y) is inside, False otherwise. Abstract method. """
        raise NotImplementedError


class RectangleBase(BaseShape):

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


class CircleBase(BaseShape):

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


class UIElement:
    """ Represents UI element """

    __slots__ = '_base_shape', '_sprite', '_state'

    def __init__(self, shape: RectangleBase, sprite: arcade.Sprite,
                 starting_state: UIElementState = UI_ELEMENT_STATE.ACTIVE):
        sprite.position = shape.position

        self._base_shape = shape
        self._sprite = sprite

        self._state = starting_state

    @property
    def position(self) -> (float, float):
        """ Return the center_x and center_y of the element """
        return self._base_shape.position

    @position.setter
    def position(self, new_value: (float, float)):
        """ Set center of the element to `new_value` """
        self._base_shape.position = new_value
        self._sprite.position = new_value

    @property
    def right(self):
        return self._base_shape.right

    @right.setter
    def right(self, new_value: float):
        self._base_shape.right = new_value
        self._sprite.right = new_value

    @property
    def left(self):
        return self._base_shape.left

    @left.setter
    def left(self, new_value: float):
        self._base_shape.left = new_value
        self._sprite.left = new_value

    @property
    def top(self):
        return self._base_shape.top

    @top.setter
    def top(self, new_value: float):
        self._base_shape.top = new_value
        self._sprite.top = new_value

    @property
    def bottom(self):
        return self._base_shape.bottom

    @bottom.setter
    def bottom(self, new_value: float):
        self._base_shape.bottom = new_value
        self._sprite.bottom = new_value

    def draw(self):
        """ Draw the element """
        _graphics_engine.draw_sprite(self)

    def get_mouse_sprite(self, state: MouseState) -> Optional[arcade.Sprite]:
        """ Return a sprite for the mouse if any """
        pass

    def on_hover(self):
        """ Handle hover event """
        pass

    def press(self):
        """ Handle pressing event """
        pass

    def release(self):
        """ Handle releasing event """
        pass

    def is_inside(self, x: float, y: float) -> bool:
        """ Return True if point (x, y) is inside, False otherwise """
        return self._base_shape.is_inside(x, y)


class UIManger:
    """ Manges UI elements (currently mouse only) """
    def __init__(self):
        self._interactable = []
        self._pressable = self._clikable = []  # clikable not implemented
        self._pressed = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        for interactable in self._interactable:
            if interactable.inside(x, y):
                _graphics_engine.mouse.set_state(MOUSE_STATE.HOVER)
                if interactable.mouse_sprite_hover:
                    _graphics_engine.mouse.set_graphic(interactable.get_mouse_sprite(MOUSE_STATE.HOVER))
                interactable.on_hover()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        for pressable in self._pressable:
            if pressable.inside(x, y):
                pressable.press()
                _graphics_engine.mouse.set_state(MOUSE_STATE.PRESS)
                if pressable.mouse_sprite_press:
                    _graphics_engine.mouse.set_graphic(pressable.get_mouse_sprite(MOUSE_STATE.PRESS))

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      buttons: int, modifiers: int):
        pass

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        return
        for pressable in self._pressed:
            pressable.release()
        _graphics_engine.mouse.set_state(MOUSE_STATE.IDLE)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        pass


class GraphicsEngine:
    """ Manages graphical effects and background/video """
    def __init__(self):
        pass

    def update(self):
        """ Update graphics to match current data """
        pass

    def force_update(self):
        pass

    def on_draw(self):
        """ Draws everything on the screen """
        from pyglet import gl
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # gl.glMatrixMode(gl.GL_MODELVIEW)
        # gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        assert _window.state == GAME_STATE.SONG_SELECT

        self._draw_fps()

        self._draw_pointer()

    def _draw_background(self):
        pass

    def _draw_pointer(self):
        """ Draw custom pointer """
        pass

    def _draw_fps(self):
        """ Show FPS on screen """
        fps = _time_engine.fps
        output = f"FPS: {fps:.1f}"
        arcade.draw_text(output, 20, _window.height // 2, arcade.color.WHITE, 16)


class SongSelect:
    """ """
    def __init__(self):
        """ """
        _window.set_state(GAME_STATE.MAIN_MENU)
        assert _window.state == GAME_STATE.MAIN_MENU

    def update(self, delta_time: float):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        """ This is called during the idle time when it should be called """
        _time_engine.tick()
        _graphics_engine.on_draw()

    def on_resize(self, width: float, height: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        pass
        if symbol == key_.NUM_ADD:
            self._audio_engine.song.volume *= 2
        if symbol == key_.NUM_SUBTRACT:
            self._audio_engine.song.volume *= 0.5
        if symbol == 99 and modifiers & 1 and modifiers & 2:
            # CTRL + SHIFT + C to close, for fullscreen emergency
            # TODO: Find a good way to exit
            pyglet.app.exit()

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        _UI_manager.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        _UI_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      buttons: int, modifiers: int):
        _UI_manager.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        _UI_manager.on_mouse_release(x, y, button, modifiers)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        _UI_manager.on_mouse_scroll(x, y, scroll_x, scroll_y)

    @property
    def update_rate(self):
        """ Return the update rate (ideal FPS) """
        return self._update_rate

    @update_rate.setter
    def update_rate(self, new_rate: float):
        """ Set the update rate (ideal FPS) """
        assert isinstance(new_rate, float)
        self._update_rate = new_rate

    @staticmethod
    def get_beatmap_filepath(song: str, difficulty: str) -> Optional[Path]:
        """ Return the filepath to .osu file given the name and
        difficulty of the song. """
        songs = Path('resources/Songs').rglob(f'*{song}*')
        try:
            for song in songs:
                if difficulty == '*' and song.suffix == '.osu':
                    return song
                if difficulty in song.name and song.suffix == '.osu':
                    return song
        except StopIteration:
            return
        return

