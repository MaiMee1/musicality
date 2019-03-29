from pathlib import Path
from typing import Any, Union, Optional, List, Dict, NewType
from random import sample

from osu import Beatmap
import key


HitObjectVar = NewType('HitObjectVar', int)
VAR_SINGLE = HitObjectVar(1)
VAR_LONG = HitObjectVar(5)


class HitObject:
    def __init__(self, song: 'Song', reach_time: int, var: HitObjectVar, symbol: int):
        self.song = song

        self.start_time = self.calculate_start_time()  # seconds
        self.reach_time = reach_time  # type: float # seconds
        self.press_time = None  # type: Optional[float]  # seconds
        self.var = var
        self.symbol = symbol

    def calculate_start_time(self) -> float:
        """ Return the start_time"""
        beat = 60 / self.song.bpm  # seconds
        delay = beat * (1 + (10 - self.song.approach_rate) / 3)  # seconds
        return self.reach_time - delay  # seconds

    def calculate_grade(self):
        # TODO
        pass

    @property
    def start_time_ms(self):
        """ Return start_time in milliseconds """
        return int(self.start_time * 1000)

    @property
    def reach_time_ms(self):
        """ Return reach_time in milliseconds """
        return int(self.reach_time * 1000)


class Song:

    DEFAULT_HIT_SOUNDS = []

    def __init__(self,
                 folder_path: Path,
                 n: int,
                 hit_sounds: Optional[list] = None):

        assert folder_path.is_dir()
        self.path = folder_path

        beatmap_list = folder_path.glob('.osu')
        beatmaps = [Beatmap(beatmap_file) for beatmap_file in beatmap_list]
        # str = beatmap.version (difficulty name)
        self.beatmaps = {}  # type: Dict[str, Beatmap]
        self.hit_objects = {}  # type: Dict[str, List[HitObject]]

        for beatmap in beatmaps:
            self.beatmaps[beatmap.version] = beatmap
            self.hit_objects[beatmap.version] = [
                HitObject(self, hit_time, VAR_SINGLE, key.K)
                for hit_time in beatmap.hit_times
            ]
        audio = beatmaps[n].audio_filepath
        bpm = beatmaps[n].BPM
        approach_rate = beatmaps[n].approach_rate
        assert bpm > 0
        assert 0 <= approach_rate <= 10
        self.audio = audio
        self.bpm = bpm
        if hit_sounds is not None:
            self.hit_sounds = hit_sounds
        else:
            self.hit_sounds = Song.DEFAULT_HIT_SOUNDS
        self.approach_rate = approach_rate



