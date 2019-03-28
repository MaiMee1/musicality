"""
Does the calculation etc.
"""
import collections
import time
from typing import Any, Union, Optional, List, Dict, NewType

import arcade.color

from keyboard import Keyboard
import key


HitObjectVar = NewType('HitObjectVar', int)
VAR_SINGLE = HitObjectVar(1)  # 1 -- 1
# 11 -- 3
VAR_LONG = HitObjectVar(5)  # 10 -- 5
# 111 -- 7


class HitObject:
    def __init__(self, reach_time: int, var: HitObjectVar, symbol: int):
        self.start_time = None  # milliseconds
        self.reach_time = reach_time  # milliseconds
        self.var = var
        self.symbol = symbol

    def set_start_time(self, bpm: float, approach_rate: float):
        assert 0 <= approach_rate <= 10
        beat = 60 / bpm  # seconds
        delay = beat * (1 + (10-approach_rate) / 3)  # seconds
        self.start_time = self.reach_time - int(delay * 1000)  # milliseconds


class Song:

    DEFAULT_HIT_SOUNDS = []

    def __init__(self,
                 audio,
                 hit_sounds: Optional[list] = None,
                 approach_rate: Optional[float] = 5):

        self.audio = audio
        if hit_sounds is not None:
            self.hit_sounds = hit_sounds
        else:
            self.hit_sounds = Song.DEFAULT_HIT_SOUNDS
        self.approach_rate = approach_rate

    def load_hit_objects(self) -> List[HitObject]:
        pass


class Main:
    """ Manages keyboard, incoming beats, etc. """
    FRAME_TIME_LEN = 60
    FRAME_RATE = 1/60

    def __init__(self, song: Song, keyboard: Keyboard):
        self.song = song
        self.keyboard = keyboard
        self.hit_objects = self.song.load_hit_objects()

        self.start_time = time.perf_counter()
        self.lag = 0

        self.old_time = self.start_time
        self.frame_times = collections.deque(maxlen=Main.FRAME_TIME_LEN)

    def update(self, delta_time: float):
        # tick
        t1 = time.perf_counter()
        dt = t1 - self.old_time
        self.old_time = t1
        self.frame_times.append(dt)

        self.lag += dt - delta_time

    def on_draw(self):
        # skip drawing this frame if lagging i.e. update again before drawing
        if self.lag > Main.FRAME_RATE:
            return


    def init_time(self):
        """ Resets time recording of this instance """
        self.frame_times = collections.deque(maxlen=Main.FRAME_TIME_LEN)
        self.lag = 0
        self.start_time = self.old_time = time.perf_counter()

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return Main.FRAME_TIME_LEN / total_time





class Audio:
    """ Manages sound, SFX, music, etc."""
    def __init__(self):
        """" loads current hit_sounds, song, fxs, """
        pass


class Graphics:
    """ Manages the drawing side of everything """
    def __init__(self):
        pass
