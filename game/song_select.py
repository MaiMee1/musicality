from __future__ import annotations

from pathlib import Path
from typing import Optional

import arcade
import pyglet

from game.constants import MouseState, MOUSE_STATE, UIElementState, UI_ELEMENT_STATE, GAME_STATE
from game.window import key as key_
from game.audio import AudioEngine, Beatmap

SCROLL_SPEED = 20

_window = None  # type: Optional[arcade.Window]

_time_engine = None  # type: Optional[TimeEngine]
_audio_engine = None  # type: Optional[AudioEngine]
_graphics_engine = None  # type: Optional[GraphicsEngine]

_UI_manager = None  # type: Optional[UIManger]


class TimeEngine:
    """ Manages time """

    __slots__ = 'time', '_frame_times', '_t', '_start_time', '_dt', '_start', '_absolute_time'

    def __init__(self, maxlen: int = 60):
        import time
        import collections
        self.time = time.perf_counter
        self._frame_times = collections.deque(maxlen=maxlen)
        # Ensure that deque is not empty and sum() != 0
        self._t = self._start_time = self._absolute_time = self.time()
        self._dt = 0
        self.tick()
        self._start = False

    def tick(self):
        """ Call to signify one frame passing """
        t = self.time()
        self._dt = dt = t - self._t
        self._t = t
        self._frame_times.append(dt)

    def start(self):
        """ Start the clock """
        self._start = True
        self._start_time = self.time()

    def reset(self):
        """ Restart the clock """
        self._start_time = self.time()

    @property
    def fps(self) -> float:
        """ Return current average fps """
        try:
            return len(self._frame_times) / sum(self._frame_times)
        except ZeroDivisionError:
            return 0

    @property
    def play_time(self) -> float:
        """ Return current time at function call in seconds """
        return self.time() - self._absolute_time

    @property
    def dt(self) -> float:
        """ Return time difference of this and last frame in seconds """
        return self._dt


class Mouse:
    def __init__(self):
        self._state = MOUSE_STATE.IDLE
        self._sprite = self.get_default_mouse_sprite()

    def get_default_mouse_sprite(self) -> arcade.Sprite:
        pass

    def draw(self):
        self._sprite.draw()

    @property
    def state(self):
        return self._state

    def set_state(self, state: MouseState):
        assert state in MOUSE_STATE
        self._state = state

    def set_graphic(self, sprite: arcade.Sprite):
        self._sprite = sprite


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

    __slots__ = '_base_shape', '_sprite', '_state', '_to_draw', 'cache', 'link'

    def __init__(self, shape: RectangleBase, sprite: arcade.Sprite,
                 starting_state: UIElementState = UI_ELEMENT_STATE.ACTIVE):
        sprite.position = shape.position

        self._base_shape = shape
        self._sprite = sprite

        self._state = starting_state
        self._to_draw = []

        self.cache = []
        self.link = None

    def add_to_draw(self, drawable):
        self._to_draw.append(drawable)

    def draw_text(self):
        text, start_x, start_y, color, font_size = self.cache
        arcade.draw_text(text, start_x, self.position[1]-font_size//2, color, font_size)

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
        self.draw_text()
        for elem in self._to_draw:
            elem.draw()

    def get_mouse_sprite(self, state: MouseState) -> Optional[arcade.Sprite]:
        """ Return a sprite for the mouse if any """
        pass

    def on_hover(self):
        """ Handle hover event """
        pass

    def press(self):
        """ Handle pressing event """
        song, difficulty = self.link
        _window.set_state(GAME_STATE.GAME_PAUSED, song=song, difficulty=difficulty)

    def release(self):
        """ Handle releasing event """
        print('release', self)

    def is_inside(self, x: float, y: float) -> bool:
        """ Return True if point (x, y) is inside, False otherwise """
        return self._base_shape.is_inside(x, y)

    @property
    def mouse_sprite_hover(self) -> None:
        return

    @property
    def mouse_sprite_press(self) -> None:
        return


class DrawableRectangle(RectangleBase):

    def __init__(self, center_x: float, center_y: float, width: float, height: float,
                 color: arcade.Color = arcade.color.BLACK, alpha: int = 255, **kwargs):
        super().__init__(center_x, center_y, width, height)

        self.border_width = kwargs.pop('border_width', 1)  # type: float
        self.tilt_angle = kwargs.pop('tilt_angle', 0)  # type: float
        self.filled = kwargs.pop('filled', True)  # type: float

        self.color = color
        self.alpha = alpha

        self.shape = None
        self.change_resolved = False
        self.recreate()

    def __str__(self):
        return f"size: {self.size} posn: {self._position}"

    def _get_opacity(self) -> float:
        return round(self.alpha / 255, 1)

    def _set_opacity(self, new_value: float):
        self.alpha = int(round(new_value * 255, 0))

    opacity = property(_get_opacity, _set_opacity)

    @property
    def rgba(self) -> arcade.Color:
        return self.color[0], self.color[1], self.color[2], self.alpha

    def draw(self):
        self.shape.draw()

    def recreate(self):
        self.shape = arcade.create_rectangle(
            self.center_x, self.center_y, self.width, self.height, self.rgba,
            self.border_width, self.tilt_angle, self.filled
        )


class UIManger:
    """ Manges UI elements (currently mouse only) """
    def __init__(self):
        self._interactable = []
        self._pressable = self._clikable = []  # clikable not implemented
        self._pressed = []

    def update(self, delta_time: float):
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        for interactable in self._interactable:
            if interactable.is_inside(x, y):
                _graphics_engine.mouse.set_state(MOUSE_STATE.HOVER)
                if interactable.mouse_sprite_hover:
                    _graphics_engine.mouse.set_graphic(interactable.get_mouse_sprite(MOUSE_STATE.HOVER))
                interactable.on_hover()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        for pressable in self._pressable:
            if pressable.is_inside(x, y):
                pressable.press()
                _graphics_engine.mouse.set_state(MOUSE_STATE.PRESS)
                if pressable.mouse_sprite_press:
                    _graphics_engine.mouse.set_graphic(pressable.get_mouse_sprite(MOUSE_STATE.PRESS))

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      buttons: int, modifiers: int):
        pass

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        for pressable in self._pressed:
            pressable.release()
        _graphics_engine.mouse.set_state(MOUSE_STATE.IDLE)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        for pressable in self._pressable:
            pressable.position = pressable.position[0], pressable.position[1] + scroll_y*SCROLL_SPEED

    def create_songs(self):
        i = 0
        for beatmap, v in self.get_beatmap_info().items():
            i += 1
            artist, song_name, difficulty, creator = v

            position = (0, 0)
            size = (600, 100)
            rec_drawable = arcade.Sprite(filename=Path('resources/song_information_sprite.jpg'))
            rec_drawable.alpha = 255
            rec_shape = RectangleBase(*position, *size)
            elem = UIElement(rec_shape, rec_drawable)
            elem.position = (_window.width-size[0]//2, 80*i)

            elem.link = song_name, difficulty

            text: str = f"{artist} - {song_name} [{difficulty}]"
            start_x = elem.left + 20
            start_y = elem.position[1]
            color = arcade.color.WHITE
            font_size = 16

            elem.cache = (text, start_x, start_y, color, font_size)

            _graphics_engine.add_element(elem)
            self._interactable.append(elem)
            self._pressable.append(elem)

    def get_beatmap_info(self):
        d = {}
        folders = Path('resources/Songs').glob("*")
        for files in [folder.rglob('*.osu') for folder in folders]:
            for file in files:
                name = file.name[:-4]
                artist = name.split(' - ')[0]
                temp = name.split(' - ')[1]
                difficulty = name.split(') [')[-1][:-1]
                temp = temp.split('(')[-1]
                creator = temp.split(') [')[0]
                temp = name.split(' - ')[1]
                song_name = temp.split(' (')[0]
                beatmap = Beatmap(file)
                d[beatmap] = artist, song_name, difficulty, creator
        return d

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


class GraphicsEngine:
    """ Manages graphical effects and background/video """
    def __init__(self):
        self._mouse = Mouse()
        self._elements = []

    @property
    def mouse(self) -> Mouse:
        return self._mouse

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
        self._draw_UI()

        self._draw_pointer()

    def add_element(self, *UI_elements: UIElement):
        for elem in UI_elements:
            assert isinstance(elem, UIElement)
        self._elements.extend(UI_elements)

    def draw_sprite(self, element: UIElement):
        element._sprite.draw()

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

    def _draw_UI(self):
        """ """
        for elem in self._elements:
            elem.draw()


class SongSelect:
    """ """
    def __init__(self, window):
        """ """
        global _window, _time_engine, _audio_engine, _graphics_engine, _UI_manager
        self._window = _window = window
        assert _window.state == GAME_STATE.SONG_SELECT

        self._time_engine = _time_engine = TimeEngine()
        self._audio_engine = _audio_engine = AudioEngine()
        self._graphics_engine = _graphics_engine = GraphicsEngine()

        self._UI_manager = _UI_manager = UIManger()

        _UI_manager.create_songs()

    def update(self, delta_time: float):
        _UI_manager.update(delta_time)

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
            _audio_engine.song.volume *= 2
        if symbol == key_.NUM_SUBTRACT:
            _audio_engine.song.volume *= 0.5
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

