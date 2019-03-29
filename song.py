from pathlib import Path
from typing import Any, Union, Optional, List, Dict, NewType
import random

from osu import Beatmap
import key


HitObjectVar = NewType('HitObjectVar', int)
VAR_SINGLE = HitObjectVar(1)
VAR_LONG = HitObjectVar(5)


def _calculate_start_time(reach_time: float, BPM: float, AR: float) -> float:
    """ Return the start_time"""
    assert BPM > 0
    assert 0 <= AR <= 10
    AR = 10
    beat = 60 / BPM  # seconds
    delay = beat * (2 + (10 - AR) / 3)  # seconds
    return reach_time - delay  # seconds


class HitObject:
    def __init__(self, beatmap: Beatmap, reach_time: int, var: HitObjectVar, symbol: int):
        self.start_time = _calculate_start_time(reach_time, beatmap.BPM, beatmap.AR)  # seconds
        self.reach_time = reach_time  # type: float # seconds
        self.press_time = None  # type: Optional[float]  # seconds
        self.var = var
        self.symbol = symbol

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
                 version: str = 'Hard',
                 hit_sounds: Optional[list] = None):

        assert folder_path.is_dir()
        self.path = folder_path
        beatmap_list = folder_path.glob('*.osu')
        beatmaps = [Beatmap(beatmap_file) for beatmap_file in beatmap_list]
        # str = beatmap.version (difficulty name)
        self.beatmaps = {}  # type: Dict[str, Beatmap]
        self.hit_objects = {}  # type: Dict[str, List[HitObject]]

        for beatmap in beatmaps:
            self.beatmaps[beatmap.version] = beatmap
            self.hit_objects[beatmap.version] = [
                HitObject(beatmap, hit_time, VAR_SINGLE, random.choice(key.normal_keys))
                for hit_time in beatmap.hit_times
            ]

        audio = self.beatmaps[version].audio_filepath
        self.audio_path = [folder_path.glob('*.mp3')][0]

        if hit_sounds is not None:
            self.hit_sounds = hit_sounds
        else:
            self.hit_sounds = Song.DEFAULT_HIT_SOUNDS



