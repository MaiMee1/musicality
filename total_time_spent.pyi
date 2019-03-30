"""
Logs total old_time I spent on the project

Mar 15, 2019 (Fri)  2 hours completing task breakdown (primary) on Trello
                    2 hours researching games
Mar 16, 2019 (Sat)  1 hour reading about arcade, openGL, and git
                    2 hours making a keyboard template on AutoCAD
                    3 hours getting started with the project + Git & GitHub
Mar 17, 2019 (Sun)  7 hours stuck with keyboard
                    2 hours digging into arcade's code and figure out how to manipulate VBOs
                    1 hour to display on-screen keyboard and fix some bugs
Mar 18, 2019 (Mon)  6 hours refactoring keyboard.py, added opacity
Mar 20, 2019 (Wed)  1/2 hour more refactoring
Mar 21, 2019 (Thu)  1/2 hour researching patterns
                    1/2 hour add key response when pressed to figure out what to do next
                    1 hour add some kind of premature graphic showing when to press, seems too
                            blocky, old_time also seems to not be constant. Seems to be working my
                            high-specs laptop a bit hard too. Should probably research about
                            multi-threading and other stuffs. Or use other alternatives such as
                            pre-made animation/video. Or textures/sprites might be a better way
                            to go about this.
Mar 22, 2019 (Fri)  2 hours Temporarily solved the FPS problem. No need to read pyglet for now.
                            (except for old_time) I guess.
Mar 23, 2019 (Sat)  2 hours refactoring things about key.
                    1/2 hour on_resize() + compatability with other computers
Mar 24, 2019 (Sun)  1 hour reading pand trying to understand pyglet.clock
Mar 25, 2019 (Mon)  2 hours re-reading style guides
                    2 hours reading about project structure
Mar 26, 2019 (Tue)  1 hour start making the XX engine (main program)?
Mar 28, 2019 (Thu)  2 hours refactoring (and broking something) getting new things ready and
                            optimizing key's animation stack
                    5 min   after showering break + Mo's advice solved the problem
Mar 29, 2019 (Fri)  5 hours botching together an update
                    4 hours rethinking, re-planning, and trying to make documentations before
                    refactoring. (DDD, I guess.)
Mar 30, 2019 (Sat)  2 hours DDD (cont.)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Union, Optional, Tuple, List, Dict, NewType

import arcade
import pyglet


class TimeEngine:
    """ Manages time """
    def __init__(self):
        pass

    def tick(self):
        """ Call to signify one frame passing """
        pass

    def fps(self) -> float:
        """ Return current average fps """
        pass

    def game_time(self) -> float:
        """ Return current game_time in seconds """
        pass

    def dt(self) -> float:
        """ Return time difference of this and last frame in seconds """
        pass


class AudioEngine:
    """ Manages audio """
    def __init__(self):
        pass

    def play(self):
        """ Play the current song and change game.state accordingly.
        Resume counting game_time. """
        pass

    def pause(self):
        """ Pause the current song and change game.state accordingly.
        Pause game_time """
        pass

    def restart(self):
        """ Reset and pause the current song and change game.state
        accordingly. Set game_time to zero - wait_time. """
        pass

    def load(self, path: Optional[Path]):
        """ Get things going. (Re)Load file from path and initialize
        for playing. Set game_time to zero - wait_time. """
        pass


class Beatmap:
    """ Represents information from .osu + .msc files """
    def __init__(self, path: Path):
        """ Load information from file at path and create appropriate
        fields. """
        pass

    def audio_path(self) -> Path:
        """ Return path to audio-- the song (mostly .mp3) --file of the
        instance. """
        pass

    def audio(self) -> pyglet.media.Source:
        """ Return an audio object that can be played, paused, replayed
        , and set time. """
        pass

    def hit_sound_paths(self) -> List[Path]:
        """ Return a list of paths to hit_sounds-- sounds a keypress
        maps to (mostly .wav) --files of the instance. """
        pass

    def hit_sounds(self) -> List[pyglet.media.Source]:
        """ Return a list of objects that can be played, paused,
        replayed, and set time. """
        pass

    def background_path(self) -> Path:
        """ Return path to background image(s?) of the instance """
        pass

    def background_image(self) -> pyglet.image.AbstractImage:
        """ Return an image that can be drawn """
        pass

    def video_path(self) -> Path:
        """ Return path to video of the instance """
        pass

    def video(self) -> pyglet.media.Source:
        """ Return a video that can be played, played, paused, replayed
        , and set time. """
        pass

    def metadata(self) -> Union[List, Tuple]:
        """ Return the metadata of the instance """
        pass

    def version(self) -> str:
        """ Return the version-- difficulty --of the instance """
        pass

    def BPM(self) -> float:
        """ Return the BPM-- beats per minute --of the instance """
        pass

    def AR(self) -> float:
        """ Return the AR-- approach rate --of the instance """
        pass

    def hit_objects(self) -> List[HitObject]:
        """ Return a list of processed hit_objects of the instance """
        pass


class HitObject:
    """ Represents an Osu! HitObject """
    def __init__(self):
        pass

    def reach_time(self) -> float:
        """ Return the time (seconds) in relation to game_time the
        instance need to be hit. """
        pass

    def reach_time_ms(self) -> int:
        """ Return the time (milliseconds) in relation to game_time the
        instance need to be hit. """
        pass

    def start_time(self) -> float:
        """ Return the time (seconds) in relation to game_time the
        instance need to start at. """
        pass

    def start_time_ms(self) -> int:
        """ Return the time (milliseconds) in relation to game_time the
        instance need to start at """
        pass

    def symbol(self) -> int:
        """ Return the symbol of the key the instance need to come in """
        pass

    def sound(self) -> pyglet.media.Source:
        """ Return a sound object that can be played """
        pass

    def state(self):
        """ Return the current state of the instance """
        pass

    def grade(self) -> Optional[str]:
        """ Return the grade-- #TODO FIND A RUBRIC --of the instance if
        gradable. None otherwise. """
        pass

    def press_time(self) -> float:
        """ Return the time (seconds) in relation to game_time the
        instance was pressed. """
        pass

    def dt(self) -> float:
        """ Return the time difference (seconds) between reach_time and
        press_time-- press_time - reach_time --of the instance.
        Negative if pressed early; positive if late. """
        pass

    def accuracy(self) -> Optional[float]:
        """ Return the accuracy-- #TODO FIND A RUBRIC --of the instance
        if graded. None otherwise. """
        pass

    def combo(self) -> int:
        """ Return combo at the time the instance was hit. Include the
        instance in the calculation as well. """
        pass


class Key:
    """ Represents a key on the virtual keyboard """
    def __init__(self):
        pass

    def update(self):
        """ Advance the instance by one frame """
        pass

    def draw(self):
        """ Draw current frame """
        pass

    def recreate_buffer(self):
        """ Create VBO object used to draw """
        pass

    def on_update(self):
        """ Do things that needs to be done and advance frame as
        appropriate. """
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        """ Handle key pressing event """
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        """ Handle key releasing event """
        pass

    def setup_animation_stack(self, style, color):
        """ Stores a VBO generator used for the animation """
        pass

    def state(self):
        """ Return the current state of the instance """
        pass


class Keyboard:
    """ Represents the board behind keys """
    def __init__(self):
        pass

    def update(self):
        """ Update the element """
        pass

    def draw(self):
        """ Draw the element """
        pass

    def recreate_buffer(self):
        """ Create VBO object used to draw """
        pass

    def location(self) -> (int, int) :
        """ Return the current location in pixels """
        pass

    def set_location(self, center_x: int, center_y: int):
        """ Move the keyboard (and its keys) to new location """
        pass


class ClockUI:
    """ Represents on-screen clock UI showing game progress """
    def __init__(self):
        pass

    def update(self):
        """ Update the element """
        pass

    def draw(self):
        """ Draw the element """
        pass


class ScoreUI:
    """ Represents on-screen score UI """
    def __init__(self):
        pass

    def update(self):
        """ Update the element's UI to match data """
        pass

    def draw(self):
        """ Draw the element """
        pass

    def score(self):
        """ Return current score """
        pass

    def __iadd__(self, other: int):
        """ Add the current score by `other` """
        pass


class ComboUI:
    """ Represents on-screen combo UI """
    def __init__(self):
        pass

    def update(self):
        """ Update the element's UI to match data """
        pass

    def draw(self):
        """ Draw the element """
        pass

    def combo(self):
        """ Return current combo """
        pass

    def break_(self):
        """ Break the current combo """
        pass

    def __iadd__(self, other: int):
        """ Add to the current combo by `other` """
        pass


class AccuracyBar:
    """ Represents on-screen accuracy bar UI """
    def __init__(self):
        pass

    def update(self):
        """ Update the element's UI to match data """
        pass

    def draw(self):
        """ Draw the element """
        pass

    def average_accuracy(self):
        """ Return current average accuracy """
        pass

    def stack_len(self):
        """ Return the number of last hit_objects used to calculate
        average_accuracy and shown on-screen. """
        pass

    def set_stack_len(self, new_len: int):
        """ Change stack_len to new_len """
        pass


class GameWindow(arcade.Window):
    def __init__(self):
        """ Create game window """
        super().__init__(1920, 1080, "musicality",
                         fullscreen=True, resizable=False, update_rate=1/60)

    def update(self, delta_time: float):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
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

    def update_rate(self):
        """ Return the current ideal update rate """
        pass

    def set_update_rate(self, rate: float):
        """ Set the update rate. Cascade throughout the objects. """
        pass

    def state(self):
        """ Return current state of the instance """
        pass

