"""
Logs total old_time I spent on the project

Mar 15, 2019 (Fri)  2 hours completing task breakdown (primary) on Trello
                    2 hours researching games
Mar 16, 2019 (Sat)  1 hour  reading about arcade, openGL, and git
                    2 hours making a keyboard template on AutoCAD
                    3 hours getting started with the project + Git & GitHub
Mar 17, 2019 (Sun)  7 hours stuck with keyboard
                    2 hours digging into arcade's code and figure out how to manipulate VBOs
                    1 hour  to display on-screen keyboard and fix some bugs
Mar 18, 2019 (Mon)  6 hours refactoring keyboard.py, added opacity
Mar 20, 2019 (Wed)  1/2 hour more refactoring
Mar 21, 2019 (Thu)  1/2 hour researching patterns
                    1/2 hour add key response when pressed to figure out what to do next
                    1 hour  add some kind of premature graphic showing when to press, seems too
                            blocky, old_time also seems to not be constant. Seems to be working my
                            high-specs laptop a bit hard too. Should probably research about
                            multi-threading and other stuffs. Or use other alternatives such as
                            pre-made animation/video. Or textures/sprites might be a better way
                            to go about this.
Mar 22, 2019 (Fri)  2 hours Temporarily solved the FPS problem. No need to read pyglet for now.
                            (except for old_time) I guess.
Mar 23, 2019 (Sat)  2 hours refactoring things about key.
                    1/2 hour on_resize() + compatability with other computers
Mar 24, 2019 (Sun)  1 hour  reading pand trying to understand pyglet.clock
Mar 25, 2019 (Mon)  2 hours re-reading style guides
                    2 hours reading about project structure
Mar 26, 2019 (Tue)  1 hour  start making the XX engine (main program)?
Mar 28, 2019 (Thu)  2 hours refactoring (and broking something) getting new things ready and
                            optimizing key's animation stack
                    5 min   after showering break + Mo's advice solved the problem
Mar 29, 2019 (Fri)  5 hours botching together an update
                    4 hours rethinking, re-planning, and trying to make documentations before
                            refactoring. (DDD, I guess.)
Mar 30, 2019 (Sat)  2 hours DDD (cont.)
Apr  5, 2019 (Fri)  10 min  TimeEngine
Apr  6, 2019 (Sat)  2 hours Audio, Time
                    30 min  Beatmap
Apr  7, 2019 (Sun)  3 hours Beatmap (cont.)
                    2 hours HitObject
Apr  8, 2019 (Mon)  2 hours Beatmap + making samples
                    1 hour  HitObject
                    2 hours ...
Ape 14, 2019 (Sun)  1 hour  ...
Ape 19, 2019 (Fri)  2 hours mapping
Apr 20, 2019 (Sat)  1 hour  mapping
                    1 hour  DDD

"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Union, Optional, Tuple, List, Dict, NewType, TextIO, Iterable, Callable

import pyglet


class TimeEngine:
    """ Manages time """
    def __init__(self, maxlen: int = 60):
        pass

    def tick(self):
        """ Call to signify one frame passing """
        pass

    @property
    def fps(self) -> float:
        """ Return current average fps """
        pass

    @property
    def game_time(self) -> float:
        """ Return current time at function call in seconds """
        pass

    @property
    def dt(self) -> float:
        """ Return time difference of this and last frame in seconds """
        pass

# helper class
class Time:
    """ Represents time. Class for conversion. """
    def __init__(self, time: Union[str, int, float]):
        """ Assume time is either (1) in seconds or (2) a string in the
        correct format. """
        pass

    def __str__(self):
        """ Return string in the format hh:mm:ss.ms """
        pass

    def __float__(self):
        """ Return time in seconds """
        pass

    def __int__(self):
        """ Return time in milliseconds """
        pass

    def __add__(self, other: Union[str, int, float]) -> Time:
        pass

    def __sub__(self, other: Union[str, int, float]) -> Time:
        pass

# helper class
class Audio:
    """ Represents an audio """

    __slots__ = '_source', '_player'

    def __init__(self, *,
                 filepath: Path = None, absolute: bool = False,
                 filename: str = '', loader: pyglet.resource.Loader = None):
        """ Load audio file from (1) filepath or (2) filename using a loader.
        Assume arguments are in the correct type. """
        pass

    @property
    def duration(self):
        """ Return length of the audio """
        pass

    def play(self):
        """ Play the audio if stopped """
        pass

    # Need to bind with a player before callable

    def stop(self):
        """ Stop the audio if playing """
        pass

    @property
    def playing(self) -> bool:
        """ Return True if audio is playing, False otherwise """
        pass

    def pause(self):
        """ Pause the audio if playing """
        pass

    def restart(self):
        """ Play the audio again from the beginning """
        pass

    @property
    def time(self) -> float:
        """ Return current time of the audio in seconds """
        pass

    @time.setter
    def time(self, new_time: Union[str, int, float]):
        """ Set current time to new_time """
        pass


class AudioEngine:
    """ Manages audio """
    def __init__(self, beatmap: Beatmap, time_engine: TimeEngine):
        pass

    def register(self, *audio: Tuple[Audio]):
        """ Register the audio file the let audio engine handle it """
        pass

    def play_sound(self, hit_sound: int):
        """ Play sounds given """
        pass

    @property
    def song(self) -> Audio:
        """ Return the song """
        pass

    def play(self, audio: Audio):
        """ Play the audio if stopped """
        pass

    def stop(self, audio: Audio):
        """ Stop the audio if playing """
        pass

    def playing(self, audio: Audio) -> bool:
        """ Return True if audio is playing, False otherwise """
        pass

    def pause(self, audio: Audio):
        """ Pause the audio if playing """
        pass

    def restart(self, audio: Audio):
        """ Play the audio again from the beginning """
        pass

    def seek(self, audio: Audio, time: Union[str, int ,float]):
        """ Seek audio to `time` """
        pass

    def time(self, audio: Audio):
        """ Return current time of audio """
        pass


class ScoreEngine:
    """ Manages calculation of score, combo, grade, etc. """
    def __init__(self, beatmap: Beatmap):
        pass

    @property
    def score(self) -> int:
        """ Returns current score """
        pass

    @property
    def combo(self) -> int:
        """ Returns current combo """
        pass

    @property
    def overall_grade(self) -> str:
        """ Returns current overall grade """
        pass

    @property
    def overall_accuracy(self) -> float:
        """ Returns current overall accuracy in percent """
        pass


class GraphicsEngine:
    """ Manages graphical effects and background/video """
    def __int__(self, beatmap: Beatmap, time_engine: TimeEngine, score_engine: ScoreEngine):
        pass

    def on_draw(self):
        """ Draws everything on the screen """
        pass

    def _draw_pointer(self):
        """ Draw custom pointer """
        pass

    def _draw_clock(self):
        """ Draw clock showing game progress """
        pass

    def _draw_combo(self):
        """ Draw current combo"""
        pass

    def _draw_score(self):
        """ Draw total score"""
        pass

    def _draw_accuracy_bar(self):
        """ Draw accuracy bar """
        pass

    def _draw_grade_fx(self, key: Key, grade):
        """ Draw fx showing grade of the beat pressed at `key`' """
        pass

    def _draw_key_press_fx(self, key: Key):
        """ Draw fx showing key pressing at `key` """
        pass

    def _draw_key_release_fx(self, key: Key):
        """ Draw fx showing key releasing at `key` """
        pass


def get_relative_path(path: Path, relative_root: Path = Path().resolve()):
    """ Return a relative path. If already relative, return unchanged """
    pass


class Beatmap:
    """ Represents information from .osu + .msc files """
    def __init__(self, filepath: Path):
        """ Load information from file at path and create appropriate
        fields. """
        pass

    @property
    def resource_loader(self):
        """ Return resource loader of folder of beatmap file """
        pass


    def get_folder_path(self, absolute=False) -> Path:
        """ Return folder path of the instance """
        pass

    def get_audio_filename(self) -> str:
        """ Return name of the audio file """
        pass

    def get_samples_filenames(self) -> List[str]:
        """ Return name of the custom sample that exists """
        pass

    def generate_video(self) -> pyglet.media.Source:
        """ Generate and return a video that can be played, played, paused, replayed
        , and set time. """
        pass

    def generate_hit_objects(self) -> List[HitObject]:
        """ Generate and return a list of processed hit_objects """
        pass

    @property
    def version(self) -> str:
        """ Return the difficulty """
        pass

    @property
    def BPM(self) -> float:
        """ Return the BPM of the version """
        pass

    @property
    def HP(self) -> float:
        """ Return the HP drain rate of the version """
        pass

    @property
    def OD(self) -> float:
        """ Return the overall difficulty of the version """
        pass

    @property
    def AR(self) -> float:
        """ Return the approach rate of the version """
        pass


class HitObject:
    """ Represents an Osu! HitObject """

    from constants import HIT_OBJECT_TYPE as TYPE, HIT_OBJECT_STATE as STATE, \
        HitObjectType as Type, HitObjectState as State

    TYPE_NAME_MAP = {
        TYPE.TAP: 'soft-hitnormal.wav',
        TYPE.HOLD: 'soft-hitwhistle.wav'
    }

    TYPE_LEN_MAP = {
        TYPE.TAP: 1,
        TYPE.HOLD: 2
    }

    def __init__(self,
                 beatmap: Beatmap,
                 time: Union[Iterable[float], float],
                 symbol: Union[Iterable[int], int],
                 note_type: Type,
                 **kwargs):
        pass

    def press(self, time: float):
        """ Mark `time` as a press_time if pressable.
        Raise TimeoutError if not pressable """
        pass

    # @property
    # def reach_times(self) -> List[float]:
    #     """ Return list of times in relation to game_time (seconds)
    #     object needs to be interacted with by the player. """
    #     pass
    #
    # @property
    # def reach_times_ms(self) -> List[int]:
    #     """ Return reach_time in milliseconds """
    #     pass

    @property
    def animation_times(self) -> List[float]:
        """ Return list of times in relation to game_time (seconds)
        graphics engine need to do animations. """
        pass

    @property
    def animation_times_ms(self) -> List[int]:
        """ Return animation_time in milliseconds """
        pass

    # @property
    # def press_times(self) -> List[float]:
    #     """ Return list of times object has been interacted with """
    #     pass
    #
    # @property
    # def press_times_ms(self) -> List[int]:
    #     """ Return press_times in milliseconds """
    #     pass

    @property
    def symbol(self) -> int:
        """ Return symbol of the key the object is scheduled to come in """
        pass

    @symbol.setter
    def symbol(self, new_symbol: int):
        """ Set symbol to new_symbol """
        pass

    @property
    def hit_sound(self) -> int:
        """ Return hit_sounds of object """
        pass

    @property
    def type(self) -> HitObject.Type:
        """ Return type of object """
        pass

    @property
    def grade(self) -> Optional[str]:
        """ Return grade of the object if graded. None otherwise. """
        pass

    @property
    def accuracy(self) -> Optional[float]:
        """ Return the accuracy of the instance if gradable.
        None otherwise. """
        pass  # TODO FIND A RUBRIC

    @property
    def state(self) -> HitObject.State:
        """ Return current state of object """
        pass

    @property
    def _dt(self) -> List[float]:
        """ Return the time difference (seconds) between reach_time and
        press_time-- press_time - reach_time --of object.
        Negative if pressed early; positive if late. """
        pass


class Key:
    """ Represents a key on the virtual keyboard """
    def __init__(self):
        self._hit_object: HitObject = HitObject()

    @property
    def hit_object(self) -> Optional[HitObject]:
        """ """
        if self._hit_object:
            return self._hit_object

    def draw(self):
        """ Draw the element """
        pass

    def press(self):
        pass

    def release(self):
        pass

    @property
    def state(self):
        """ Return the current state of the key """
        pass


class Keyboard:
    """ Represents the board behind keys """
    def __init__(self):
        self.keys: Dict[int, Key] = {}

    def draw(self):
        """ Draw the element """
        pass

    def location(self) -> (int, int) :
        """ Return the current location in pixels """
        pass

    def set_location(self, center_x: int, center_y: int):
        """ Move the keyboard (and its keys) to new location """
        pass


class AccuracyBar:
    """ Represents on-screen accuracy bar """
    def __init__(self):
        pass

    def draw(self):
        """ Draw the graphical representation of the element """
        pass

    @property
    def average_accuracy(self):
        """ Return current average accuracy """
        pass

    @property
    def stack_len(self):
        """ Return the number of last hit_objects used to calculate
        average_accuracy and shown on-screen. """
        pass

    @stack_len.setter
    def stack_len(self, new_len: int):
        """ Change stack_len to new_len """
        pass

    def add(self, accuracy: float):
        """ Add new accuracy to bar """
        pass


from constants import GameState, GAME_STATE


class Game:
    """ Main application class """
    def __int__(self, song: str, difficulty: str):
        pass

    def update(self, delta_time: float):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        """ This is called during the idle time when it should be called """
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      buttons: int, modifiers: int):
        pass

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        pass

    def set_update_rate(self, rate: float):
        """ Set the update rate. Cascade throughout the objects. """
        pass

    @property
    def state(self) -> GameState:
        """ Return current state of the instance """
        pass

    def _change_state(self, new_state: GameState):
        """ Change current state to new_state """
        pass

    def get_beatmap_filepath(self, song: str, difficulty: str) -> Path:
        """ Return the filepath to .osu file given the name and
        difficulty of the song. """
        pass