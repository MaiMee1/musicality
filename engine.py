"""
Does the calculation etc.
"""
from typing import Any, Union, Optional, Dict, NewType

import arcade.color

from keyboard import Keyboard
import key


HitObjectVar = NewType('HitObjectVar', int)
VAR_SINGLE = HitObjectVar(1)  # 1 -- 1
# 11 -- 3
VAR_LONG = HitObjectVar(5)  # 10 -- 5
# 111 -- 7


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


class Main:
    """ Manages keyboard, incoming beats, etc. """
    def __init__(self, song: Song, keyboard: Keyboard):
        pass

    def update(self, delta_time: float):
        pass


class Audio:
    """ Manages sound, SFX, music, etc."""
    def __init__(self):
        """" loads current hit_sounds, song, fxs, """
        pass


class Graphics:
    """ Manages the drawing side of everything """
    def __init__(self):
        pass
