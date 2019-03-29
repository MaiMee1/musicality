"""
Does the calculation etc.
"""
import collections
import time
from typing import Any, Union, Optional, List, Dict, NewType
from pathlib import Path

import arcade.color

from keyboard import Keyboard
from song import Song
import key


HitObjectVar = NewType('HitObjectVar', int)
VAR_SINGLE = HitObjectVar(1)
VAR_LONG = HitObjectVar(5)


class Main:
    """ Manages keyboard, incoming beats, etc. """
    FRAME_TIME_LEN = 60
    FRAME_RATE = 1/60

    def __init__(self, song_folder: Path, keyboard: Keyboard):
        version = 'Hard'
        self.song = Song(song_folder, version)
        self.keyboard = keyboard
        self.incoming_hit_objects = self.hit_objects = self.song.hit_objects[version]
        self.send_hit_objects = []

        self.lag = 0

        self.frame_times = collections.deque(maxlen=Main.FRAME_TIME_LEN)
        self.old_time = self.start_time = time.perf_counter()

        self.start = False

    def update(self, delta_time: float):
        # tick
        t1 = time.perf_counter()
        dt = t1 - self.old_time
        self.old_time = t1
        self.frame_times.append(dt)
        self.lag += dt - delta_time

        if self.start:
            send = []
            for hit_object in self.incoming_hit_objects:
                if self.time >= hit_object.start_time:
                    self.keyboard.send(hit_object)
                    send.append(hit_object)
                else:
                    break
            self.send_hit_objects.extend(send)
            for hit_object in send:
                self.incoming_hit_objects.remove(hit_object)

        self.keyboard.update()

    def on_draw(self):
        # HACK skip drawing this frame if lagging i.e. update again before drawing
        if self.lag > Main.FRAME_RATE:
            print(self.lag)
            return
        self.keyboard.draw()

    @property
    def time(self) -> float:  # seconds
        return self.old_time - self.start_time

    def init_game(self):
        """ Resets time recording of this instance """
        self.frame_times = collections.deque(maxlen=Main.FRAME_TIME_LEN)
        self.lag = 0
        self.start_time = self.old_time = time.perf_counter()

        self.start = True

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return Main.FRAME_TIME_LEN / total_time

    def on_key_press(self, symbol: int, modifiers: int):
        self.keyboard.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.keyboard.on_key_release(symbol, modifiers)


class Audio:
    """ Manages sound, SFX, music, etc."""
    def __init__(self):
        """" loads current hit_sounds, song, fxs, """
        pass


class Graphics:
    """ Manages the drawing side of everything """
    def __init__(self):
        pass
