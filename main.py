from __future__ import annotations

from pathlib import Path
from io import StringIO
from typing import Any, Union, Optional, Tuple, List, Dict, NewType, TextIO, Iterable, Callable, Hashable
import warnings
from random import random

import arcade
import pyglet

import key as key_
from keyboard import Keyboard, Key
import keyboard as keyboard_
from type_ import *
from constants import MouseState, MOUSE_STATE, UIElementState, UI_ELEMENT_STATE

from audio import Beatmap, AudioEngine, HitObject
# TODO how to play

_window = None  # type: Optional[arcade.Window]

_time_engine = None  # type: Optional[TimeEngine]
_audio_engine = None  # type: Optional[AudioEngine]
_graphics_engine = None  # type: Optional[GraphicsEngine]

_score_manager = None  # type: Optional[ScoreManager]
_hit_object_manager = None  # type: Optional[HitObjectManager]
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
    def game_time(self) -> float:
        """ Return current time at function call in seconds """
        try:
            assert self._start
            return _audio_engine.song.time
        except AssertionError:
            return 0

    @property
    def play_time(self) -> float:
        """ Return current time at function call in seconds """
        return self.time() - self._absolute_time

    @property
    def dt(self) -> float:
        """ Return time difference of this and last frame in seconds """
        return self._dt


class ScoreManager:
    """ Manages calculation of score, combo, grade, etc. """
    def __init__(self, beatmap: Beatmap):
        from collections import deque
        self._beatmap = beatmap
        self._score = 0
        self._combo = [0]
        self._perfect = True
        self._not_missed = True
        self._accuracy_stack = deque(maxlen=20)
        self._abs_accuracy_stack = []

    def register_hit(self, hit_object: HitObject, time: float, type: HitObject.Type):
        """ `time` = -1 for misses """
        # TODO
        ideal = hit_object.get_reach_time()
        assert ideal is not None
        accuracy = self._calculate_accuracy(ideal, time)
        grade = self._calculate_grade(accuracy)
        score = self._calculate_score(grade, type)

        self._accuracy_stack.append(accuracy)
        print(1 - abs(accuracy))
        self._abs_accuracy_stack.append(1 - abs(accuracy))
        if self._perfect:
            if grade != 'perfect':
                self._perfect = False
        if grade == 'miss':
            self._break_combo()
            if self._not_missed:
                self._not_missed = False
        else:
            self._combo[-1] += 1
        hit_object.add_grade(grade)
        self._score += score

    def _calculate_accuracy(self, ideal: float, time: float) -> float:
        dt = time - ideal
        ac = dt / 0.5
        if ac > 1:
            ac = 1
        elif ac < -1:
            ac = -1
        return ac

    def _calculate_grade(self, accuracy: float) -> str:
        abs_dt = abs(accuracy)
        if abs_dt >= 1:
            return 'miss'
        if abs_dt >= 0.5:
            return 'bad'
        if abs_dt >= 0.3:
            return 'ok'
        if abs_dt >= 0.2:
            return 'good'
        if abs_dt >= 0.1:
            return 'almost'
        return 'perfect'

    def _calculate_score(self, grade: str, type: HitObject.Type):
        combo_bonus = (self.combo // 10) * 80
        if grade == 'perfect':
            return 300
        if grade == 'almost':
            return 300
        if grade == 'good':
            return 200
        if grade == 'ok':
            return 100
        if grade == 'bad':
            return 50
        return 1

    @property
    def score(self) -> int:
        """ Returns current score """
        return self._score

    @property
    def combo(self) -> int:
        """ Returns current combo """
        return self._combo[-1]

    def _break_combo(self):
        self._combo.append(0)

    @property
    def overall_grade(self) -> str:
        """ Returns current overall grade """
        if self._perfect:
            return 'SS'
        if self._not_missed:
            return 'S'
        ac = self.overall_accuracy
        if ac >= 0.8:
            return 'A'
        if ac >= 0.7:
            return 'B'
        if ac >= 0.6:
            return 'C'
        if ac >= 0.5:
            return 'D'
        return 'F'

    @property
    def overall_accuracy(self) -> float:
        """ Returns current overall accuracy in percent """
        try:
            return sum(self._abs_accuracy_stack) / len(self._abs_accuracy_stack)
        except ZeroDivisionError:
            return 1

    @property
    def current_accuracies(self) -> Iterable[float]:
        """ Returns current accuracies in accuracy """
        return self._accuracy_stack

    @property
    def current_accuracy(self) -> Iterable[float]:
        """ Returns instantaneous accuracy in accuracy """
        raise NotImplementedError


class FX:
    """ Represents a graphical fx """
    def __init__(self, start_time: float, finish_time: float, draw_function: callable, object_with_references: Iterable, *args):
        """ :param args: draw function's arguments """
        self._start_time = start_time
        self._finish_time = finish_time
        self._draw = draw_function
        self.args = args
        self._object_with_references = object_with_references

    def draw(self):
        elapsed = _time_engine.game_time - self._start_time
        total = self._finish_time - self._start_time
        self._draw(*self.args, fps=_time_engine.fps, elapsed=elapsed, total=total)

    @property
    def start_time(self):
        return self._start_time

    @property
    def finish_time(self):
        return self._finish_time

    def kill(self):
        raise NotImplementedError


class GraphicsEngine:
    """ Manages graphical effects and background/video """

    from io import BytesIO

    import arcade.color as COLOR
    from io import BytesIO
    from random import randint

    __slots__ = '_beatmap', '_keyboard', '_game', '_fxs', '_current_time', '_bg', '_video_player', '_video'

    def __init__(self):
        self._fxs = {}  # type: Dict[object, List[FX]]
        self._current_time = 0
        self._keyboard = None
        self._bg = None
        self._video = None
        self._video_player = None

    def load_beatmap(self, beatmap: Beatmap):
        """ Call this each game """
        self._beatmap = beatmap
        self._video = beatmap.generate_video()

        path = self._beatmap.get_folder_path() / self._beatmap.background_filename
        self._bg = arcade.load_texture(file_name=path.as_posix())

    def set_keyboard(self, keyboard: Keyboard):
        """ Call this each game """
        self._keyboard = keyboard
        keyboard.set_graphics_engine(self)

    def update(self):
        """ Update graphics to match current data """
        self._current_time = _time_engine.game_time
        for fxs in self._fxs.values():
            if fxs[0].finish_time < self._current_time:
                discard = fxs.pop(0)

    def force_update(self):
        self._keyboard.change_resolved = False
        for key in self._keyboard.keys.values():
            key.change_resolved = False

    def on_draw(self):
        """ Draws everything on the screen """
        from pyglet import gl
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # gl.glMatrixMode(gl.GL_MODELVIEW)
        # gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        if _window.state in (GAME_STATE.GAME_PAUSED, GAME_STATE.GAME_PLAYING, GAME_STATE.GAME_FINISH):

            if self._video_player:
                if self._video_player.source:
                    self._draw_video()
            elif self._bg:
                self._draw_background()

            if _window.state == GAME_STATE.GAME_PLAYING or _window.state == GAME_STATE.GAME_PAUSED:
                if self._keyboard:
                    self._draw_keyboard()

            self._draw_fx()

            self._draw_clock()
            self._draw_combo()
            self._draw_score()
            self._draw_total_accuracy()
            self._draw_overall_grade()
            self._draw_accuracy_bar()

            self._draw_game_time()

        self._draw_fps()

        self._draw_pointer()

    def _draw_background(self):
        scale = min(_window.width / self._bg.width, _window.height / self._bg.height)
        self._bg.draw(_window.width//2, _window.height//2, self._bg.width*scale, self._bg.height*scale)

    def start_video(self):
        return
        if self._video:
            self._video_player = pyglet.media.Player()
            self._video_player.queue(self._video)
            self._video_player.play()

    def _draw_video(self):
        a = self._video_player.texture

        frame_stream = GraphicsEngine.BytesIO()
        a.save(filename=f'{str(hash(GraphicsEngine.randint))[:10]}.png', file=frame_stream, encoder=None)
        # frame = arcade.Image.open(frame_stream)
        # noinspection PyTypeChecker
        bg = arcade.load_texture(file_name=frame_stream)
        bg.draw(_window.width//2, _window.height//2, bg.width, bg.height)

    def _draw_keyboard(self):
        """ Draw keyboard """
        keyboard = self._keyboard

        if not keyboard.change_resolved:
            keyboard.shape = arcade.create_rectangle(
                keyboard.center_x, keyboard.center_y, keyboard.width, keyboard.height, keyboard.rgba,
                border_width=keyboard.border_width, tilt_angle=keyboard.tilt_angle, filled=keyboard.filled)
            keyboard.change_resolved = True

        for key in self._keyboard.keys.values():
            if not key.change_resolved:
                key.shape = arcade.create_rectangle(
                    key.center_x, key.center_y, key.width, key.height, key.rgba,
                    border_width=key.border_width, tilt_angle=key.tilt_angle, filled=key.filled)
                key.change_resolved = True

        for shape in [keyboard.shape] + [key.shape for key in keyboard.keys.values()]:
            shape.draw()

        for key in keyboard.keys.values():
            # FIXME pyglet draw doesn't work in arcade
            if key.graphic:
                key.graphic.draw()
            else:
                if key.graphic is None:
                    try:
                        text = key_.MAP_SYMBOL_TEXT[key.symbol]
                        multiline = False
                        if '\n' in text:
                            multiline = True
                        label = pyglet.text.Label(
                            text, 'Montserrat', key.height//2, color=(255, 255, 255, 255),
                            x=key.position[0], y=key.position[1], anchor_x='center', anchor_y='center',
                            multiline=multiline)
                        key.graphic = label
                        key.graphic.draw()
                    except KeyError:
                        key.graphic = 0

    def _register_fx(self, fxs: List[FX], hash=None):
        """ Add `fx` to to-draw stack """
        if hash is None:
            number = _time_engine.game_time + random()
            self._fxs[number.__hash__()] = fxs
        else:
            self._fxs[hash] = fxs

    def remove_fx(self, *, fxs: List[FX] = None, hash=None):
        if hash is not None:
            try:
                self._fxs.pop(hash)
            except KeyError:
                print('KeyError')
        else:
            # FIXME
            print('else')
            to_remove = []
            for k, v in self._fxs.items():
                if v == fxs:
                    to_remove.append(k)
            for elem in to_remove:
                self._fxs.pop(elem)

            # raise AssertionError

    def _draw_fx(self):
        """ Draw fx that are on-going """
        copy = [_ for _ in self._fxs.values()]
        for fxs in copy:
            try:
                fxs[0].draw()
            except IndexError:
                self.remove_fx(fxs=fxs)

    def add_grade_fx(self, key: Key, grade):
        """ Draw fx showing grade of the beat pressed at `key`' """
        pass

    def add_key_press_fx(self, key: Key):
        """ Draw fx showing key pressing at `key` """
        pass

    def add_key_release_fx(self, key: Key):
        """ Draw fx showing key releasing at `key` """
        pass

    def add_hit_object_animation(self, key: Key, hit_object: HitObject):
        """ Draw incoming hit_object """
        in_, out = self.create_incoming_fx(key, hit_object)
        self._register_fx([in_, out], hit_object)

    def create_incoming_fx(self, key: Key, hit_object: HitObject) -> Iterable[FX]:
        def f(*args, **kwargs):
            center_x, center_y, width, height, rgba, tilt_angle = args

            elapsed = kwargs.pop('elapsed', None)
            total = kwargs.pop('total', None)

            if elapsed > total:
                return

            arcade.draw_rectangle_filled(center_x, center_y,
                                         width * elapsed / total,
                                         height * elapsed / total,
                                         rgba,
                                         tilt_angle=tilt_angle)

        def g(*args, **kwargs):
            center_x, center_y, width, height, rgba, tilt_angle = args
            try:
                r, g, b = rgba
                a = 255
            except ValueError:
                r, g, b, a = rgba

            elapsed = kwargs.pop('elapsed', None)
            total = kwargs.pop('total', None)

            if elapsed > total:
                print('elapsed > total')
                return

            arcade.draw_rectangle_filled(center_x, center_y,
                                         width,
                                         height,
                                         (r, g, b, a*(1 - elapsed/total)),
                                         tilt_angle=tilt_angle)


        rgba_ = GraphicsEngine.COLOR.PINK

        fx = FX(self._current_time, hit_object.reach_times[0], f, [key],
                key.center_x, key.center_y, key.width, key.height, rgba_, key.tilt_angle)
        end_fx = FX(hit_object.reach_times[0], hit_object.reach_times[0] + 0.195, g, [key],
                key.center_x, key.center_y, key.width, key.height, rgba_, key.tilt_angle)
        return fx, end_fx

    def _draw_pointer(self):
        """ Draw custom pointer """
        pass

    def _draw_clock(self):
        """ Draw clock showing game progress """
        pass

    def _draw_combo(self):
        """ Draw current combo"""
        if _score_manager:
            combo = _score_manager.combo
            output = f"combo: {combo}"
            arcade.draw_text(output, 20, _window.height // 2 - 60, arcade.color.WHITE, 16)

    def _draw_score(self):
        """ Draw total score"""
        if _score_manager:
            score = _score_manager.score
            output = f"score: {score}"
            arcade.draw_text(output, 20, _window.height // 2 + 30, arcade.color.WHITE, 16)

    def _draw_total_accuracy(self):
        """ Draw total accuracy """
        if _score_manager:
            ac = _score_manager.overall_accuracy
            output = f"accuracy: {ac*100:.0f}%"
            arcade.draw_text(output, 20, _window.height // 2 - 120, arcade.color.WHITE, 16)

    def _draw_overall_grade(self):
        """ Draw overall grade """
        if _score_manager:
            grade = _score_manager.overall_grade
            output = f"grade: {grade}"
            arcade.draw_text(output, 20, _window.height // 2 - 90, arcade.color.WHITE, 16)

    def _draw_accuracy_bar(self):
        """ Draw accuracy bar """
        pass

    def _draw_fps(self):
        """ Show FPS on screen """
        fps = _time_engine.fps
        output = f"FPS: {fps:.1f}"
        arcade.draw_text(output, 20, _window.height // 2, arcade.color.WHITE, 16)

    def _draw_game_time(self):
        """  """
        time = _time_engine.game_time
        output = f"audio time: {time:.3f}"
        arcade.draw_text(output, 20, _window.height // 2 - 30, arcade.color.WHITE, 16)


class HitObjectManager:
    """ Manages sending hit_objects to keys and GraphicEngine"""
    def __init__(self, hit_objects: List[HitObject], keyboard: Keyboard):
        self._keys = keyboard.keys
        self._incoming = self._hit_objects = hit_objects
        self._sent = []  # type: List[HitObject]
        self._passed = []  # type: List[HitObject]

    def update(self):
        time = _time_engine.game_time
        send = []
        for hit_object in self._incoming:
            if time >= hit_object.animation_times[0]:
                key = self._keys[hit_object.symbol]
                key.hit_object = hit_object
                _graphics_engine.add_hit_object_animation(key, hit_object)
                hit_object.change_state('active')
                send.append(hit_object)
        for hit_object in self._sent:
            if time > hit_object.reach_times[-1] + 0.2:
                if hit_object.state != HitObject.STATE.PASSED:
                    self._change_stack_and_remove_fx(hit_object)
                    _score_manager.register_hit(hit_object, -1, hit_object.type)
                    key = self._keys[hit_object.symbol]
                    key.remove_hit_object()
                    hit_object.change_state('passed')
        if send:
            for elem in send:
                self._incoming.remove(elem)
            self._sent.extend(send)

    def _change_stack_and_remove_fx(self, hit_object: HitObject):
        for elem in self._sent.copy():
            if elem == hit_object:
                self._sent.remove(hit_object)
                self._passed.append(hit_object)
                _graphics_engine.remove_fx(hash=hit_object)

    def on_key_press(self, symbol: int, modifiers: int):
        try:
            key = self._keys[symbol]
        except KeyError:
            key = None
        hit_object = None  # type: Optional[HitObject]
        if key:
            key.press()
            try:
                hit_object = key.hit_object
            except AttributeError:
                print('no object')
        if hit_object:
            _audio_engine.play_sound(*hit_object.hit_sound)
            try:
                time = _time_engine.game_time
                hit_object.press(time)
                _score_manager.register_hit(hit_object, time, hit_object.type)
                assert hit_object.state == HitObject.STATE.PASSED
                if hit_object.state == HitObject.STATE.PASSED:
                    _graphics_engine.remove_fx(hash=hit_object)
                    key.remove_hit_object()
            except TimeoutError:
                self._change_stack_and_remove_fx(hit_object)
                key.remove_hit_object()
                _graphics_engine.remove_fx(hash=hit_object)

    def on_key_release(self, symbol: int, modifiers: int):
        try:
            key = self._keys[symbol]
        except KeyError:
            key = None
        if key:
            try:
                key.hit_object.press(_time_engine.game_time)
            except TimeoutError:
                assert False, 'Dont reach this'
                self._change_stack_and_remove_fx(key.hit_object)
                key.remove_hit_object()
            except AttributeError:
                pass


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


class Game:
    """ """
    def __init__(self, width, height, song: str, difficulty: str):
        """ """
        global _score_manager, _hit_object_manager, _UI_manager
        filepath = self.get_beatmap_filepath(song, difficulty)
        if filepath is None:
            raise AssertionError
        self._beatmap = Beatmap(filepath)

        keyboard_.set_scaling(5)
        self._keyboard = Keyboard(width//2, height//2, model='small notebook', color=arcade.color.LIGHT_BLUE, alpha=150)

        _score_manager = self._score_manager = ScoreManager(beatmap=self._beatmap)
        self._hit_objects = self._beatmap.generate_hit_objects()
        _hit_object_manager = self._hit_object_manager = HitObjectManager(hit_objects=self._hit_objects, keyboard=self._keyboard)
        _UI_manager = self._UI_manager = UIManger()

        self._time_engine = _time_engine
        self._audio_engine = _audio_engine
        self._graphics_engine = _graphics_engine

        for elem in (_audio_engine, _graphics_engine):
            elem.load_beatmap(self._beatmap)

        _graphics_engine.set_keyboard(self._keyboard)

        self._update_rate = 1/60
        assert _window.state == GAME_STATE.GAME_PAUSED

    def start(self):
        """ Start the game """
        _window.set_state(GAME_STATE.GAME_PLAYING)
        self._audio_engine.song.play()
        self._graphics_engine.start_video()
        self._time_engine.start()

    def finish(self):
        """ Stop the game """
        _window.set_state(GAME_STATE.GAME_FINISH)

    def pause(self):
        """ Pause the game """
        pass

    def update(self, delta_time: float):
        self._hit_object_manager.update()
        self._graphics_engine.update()
        if not self._audio_engine.song.playing:
            if _window.state == GAME_STATE.GAME_PLAYING:
                self.finish()

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        """ This is called during the idle time when it should be called """
        self._time_engine.tick()
        self._graphics_engine.on_draw()

    def on_resize(self, width: float, height: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key_.P:
            if _window.state != GAME_STATE.GAME_PLAYING:
                self.start()
        if symbol == key_.NUM_ADD:
            self._audio_engine.song.volume *= 2
        if symbol == key_.NUM_SUBTRACT:
            self._audio_engine.song.volume *= 0.5
        if symbol == 99 and modifiers & 1 and modifiers & 2:
            # CTRL + SHIFT + C to close, for fullscreen emergency
            # TODO: Find a good way to exit
            pyglet.app.exit()

        self._hit_object_manager.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        try:
            key = self._keyboard.keys[symbol]
        except KeyError:
            key = None
        if key:
            key.release()
            hit_object = key.hit_object
            if hit_object:
                if hit_object.type == HitObject.TYPE.HOLD:
                    hit_object.press(self._time_engine.game_time)

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


def swap_codecs():
    """ Because pyglet is still buggy we need this to ensure ffmpeg is used """
    decoders = pyglet.media.codecs._decoders
    assert "pyglet.media.codecs.ffmpeg.FFmpegDecoder" in str(decoders)  # assure that it exists
    while str(decoders[0])[:41] != "<pyglet.media.codecs.ffmpeg.FFmpegDecoder":
        # cycle until decoder is ffmpeg
        temp = decoders.pop(0)
        decoders.append(temp)


from constants import GAME_STATE, GameState


class SongSelect:

    def __init__(self):
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


class GameWindow(arcade.Window):
    def __init__(self):
        """ Create game window """
        global _time_engine, _audio_engine, _graphics_engine, _window
        super().__init__(1920, 1080, "musicality",
                         fullscreen=False, resizable=True, update_rate=1/60)
        arcade.set_background_color(arcade.color.BLACK)

        swap_codecs()

        _window = self
        _time_engine = TimeEngine()
        _audio_engine = AudioEngine()
        _graphics_engine = GraphicsEngine()

        self._state = GAME_STATE.MAIN_MENU
        # self.song_select = SongSelect()
        self._state = GAME_STATE.GAME_PAUSED
        self.game = Game(1920, 1080, 'MONSTER', 'NORMAL')

        self.handler = self.game

    def update(self, delta_time: float):
        self.handler.update(delta_time)

    def on_update(self, delta_time: float):
        self.handler.on_update(delta_time)

    def on_draw(self):
        self.handler.on_draw()

    def on_resize(self, width: float, height: float):
        self.handler.on_resize(width, height)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.handler.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol: int, modifiers: int):
        self.handler.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.handler.on_key_release(symbol, modifiers)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.handler.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      buttons: int, modifiers: int):
        self.handler.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.handler.on_mouse_release(x, y, button, modifiers)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.handler.on_mouse_scroll(x, y, scroll_x, scroll_y)

    @property
    def state(self):
        """ Return current state of the instance """
        return self._state

    def set_state(self, state: GameState, **kwargs):
        self._state = state
        if state == GAME_STATE.GAME_PAUSED:
            song = kwargs.pop('song', None)
            difficulty = kwargs.pop('difficulty', None)
            assert song is not None
            assert difficulty is not None
            self.handler = self.game = Game(1920, 1080, song, difficulty)


def main():
    global _window
    _window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
