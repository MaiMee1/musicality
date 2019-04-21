# from __future__ import annotations
from pathlib import Path
from io import StringIO
from typing import Union, TextIO

from osu.constants import *

OSU_FILE_FORMAT = 'v14'


class General:

    def __init__(self, **kw):

        self.audio_filename = 'audio_path.mp3'
        self.audio_lead_in = 0
        self.preview_time = -1
        self.countdown = 1
        self.sample_set = SAMPLE_SET.NORMAL
        self.stack_leniency = 0.7
        self.mode = 0
        self.letterbox_in_breaks = 0
        self.widescreen_storyboard = 0

        for k, v in kw.items():
            if k not in self.__dict__.keys():
                raise TypeError("__init__() got an unexpected keyword argument '{}'.\n"
                                "Valid options are:{}".format(k, ' -'.join(self.__dict__.keys())))
            setattr(self, k, v)

    def __str__(self):
        return f'[General]\n' \
               f'AudioFilename: {self.audio_filename}\n' \
               f'AudioLeadIn: {self.audio_lead_in}\n' \
               f'PreviewTime: {self.preview_time}\n' \
               f'Countdown: {self.countdown}\n' \
               f'sampleSet: {self.sample_set}\n' \
               f'StackLeniency: {self.stack_leniency}\n' \
               f'Mode: {self.mode}\n' \
               f'LetterboxInBreaks: {self.letterbox_in_breaks}\n' \
               f'WidescreenStoryboard: {self.widescreen_storyboard}'


class Editor:

    def __init__(self, **kw):
        self.distance_spacing = 0.8
        self.beat_divisor = 1
        self.grid_size = 4
        self.timeline_zoom = 1

        for k, v in kw.items():
            if k not in self.__dict__.keys():
                raise TypeError("__init__() got an unexpected keyword argument '{}'.\n"
                                "Valid options are:{}".format(k, ' -'.join(self.__dict__.keys())))
            setattr(self, k, v)

    def __str__(self):
        return f'[Editor]\n' \
               f'DistanceSpacing: {self.distance_spacing}\n' \
               f'BeatDivisor: {self.beat_divisor}\n' \
               f'GridSize: {self.grid_size}\n' \
               f'TimelineZoom: {self.timeline_zoom}'


class Metadata:

    def __init__(self, **kw):

        self.title = ''
        self.title_unicode = None
        self.artist = ''
        self.artist_unicode = None
        self.creator = ''
        self.version = VERSION.EASY
        self.source = ''
        self.tags = ''
        self.beatmap_id = 0
        self.beatmap_set_id = -1

        for k, v in kw.items():
            if k not in self.__dict__.keys():
                raise TypeError("__init__() got an unexpected keyword argument '{}'.\n"
                                "Valid options are:{}".format(k, ' -'.join(self.__dict__.keys())))
            setattr(self, k, v)

        if self.title_unicode is None and self.title != '':
            self.title_unicode = self.title
        if self.artist_unicode is None and self.artist != '':
            self.artist_unicode = self.artist

    def __str__(self):
        return f'[Metadata]\n' \
               f'Title:{self.title}\n' \
               f'TitleUnicode:{self.title_unicode}\n' \
               f'Artist:{self.artist_unicode}\n' \
               f'ArtistUnicode:{self.artist_unicode}\n' \
               f'Creator:{self.creator}\n' \
               f'Version:{self.version}\n' \
               f'Source:{self.source}\n' \
               f'Tags:{" ".join(self.tags)}\n' \
               f'BeatmapID:{self.beatmap_id}\n' \
               f'BeatmapSetID:{self.beatmap_set_id}\n'


class Difficulty:

    def __init__(self, **kw):
        self.hp = 5
        self.cs = 5
        self.od = 5
        self.ar = 5
        self.slider_multiplier = 1.4
        self.slider_tick_rate = 1

        for k, v in kw.items():
            if k not in self.__dict__.keys():
                raise TypeError("__init__() got an unexpected keyword argument '{}'.\n"
                                "Valid options are:{}".format(k, ' -'.join(self.__dict__.keys())))
            setattr(self, k, v)

    def __str__(self):
        return f'[Difficulty]\n' \
               f'HPDrainRate:{self.hp}\n' \
               f'CircleSize:{self.cs}\n' \
               f'OverallDifficulty:{self.od}\n' \
               f'ApproachRate:{self.ar}\n' \
               f'SliderMultiplier:{self.slider_multiplier}\n' \
               f'SliderTickRate:{self.slider_tick_rate}\n'


class Events:

    def __init__(self):
        pass

    def __str__(self):
        return f'//Background and Video events\n' \
               f'//Break Periods\n' \
               f'//Storyboard Layer 0 (Background)\n' \
               f'//Storyboard Layer 1 (Fail)\n' \
               f'//Storyboard Layer 2 (Pass)\n' \
               f'//Storyboard Layer 3 (Foreground)\n' \
               f'//Storyboard sound Samples\n'


class TimingPoint:

    def __init__(self):
        self.offset = 0  # time
        self.BPM = 15
        self.slider_velocity_multiplier = 1.00
        self.time_signature = 4  # ? / 4
        self.sample = DEFAULT_SAMPLE  # Normal -> 1 Soft -> 2
        # ? TODO
        self.volume = DEFAULT_VOLUME
        self.inherit = 0  # 1 -> Timing point  0 -> Inherited point
        self.kiai = OFF  # 1 -> on  0 -> off

    def __str__(self):
        # Timing Point
        if self.inherit == 1:
            return f'{self.offset},{60000 / self.BPM},{self.time_signature},{self.sample},' \
                   f'{1},{self.volume},{self.inherit},{self.kiai}'
        # Inherited point
        return f'{self.offset},{-100 / self.slider_velocity_multiplier},{self.time_signature},{self.sample},' \
               f'{1},{self.volume},{self.inherit},{self.kiai}'

    # def __init__(self):
    #     self.points = []  # list of TimingPoint
    # FIXME
    # def __str__(self):
    #     msg = ''
    #     for point in self.points:
    #         msg = msg + str(point) + '\n'
    #     return f'[TimingPoints]\n' + msg


class Colours:

    class Colour:

        def __init__(self, red=0, green=0, blue=0):
            self.red = red
            self.green = green
            self.blue = blue

        def __str__(self):
            return str(self.red) + ',' + str(self.green) + ',' + str(self.blue)

    def __init__(self):
        self.combos = [self.Colour(), self.Colour(), self.Colour(), self.Colour()]

    def __str__(self):
        msg = ''
        for i in range(len(self.combos)):
            msg = msg + f'Combo{i+1} : {self.combos[i]}'
        return f'[Colours]\n' + msg


class HitObject:
    """ Constants used: SOUND, """
    SOUND_ADDITION = {'Clap': 8, 'Finish': 4, 'Whistle': 2, None: 0}
    TYPE = (CIRCLE, SLIDER, SPINNER)

    def __init__(self, x: int, y: int, time: int, type: int = 1):
        self.x = x
        self.y = y
        self.time = time
        self.combo_index = type  # CIRCLE, SLIDER, SPINNER
        self.sound_addition = 0  # 0, 2, 4, 8, 6, 10, 12, 14
        self.end_time = None
        # TODO
        self.x1
        self.x2
        self.x3
        self.x4
        self.sampleset = 0  # sound_dict
        self.additions = 0  # sound_dict
        self.xxxx = [self.sampleset, self.additions, 0, 0]

    @property
    def type(self):
        if self.combo_index in CIRCLE: return 'CIRCLE'
        if self.combo_index in SLIDER: return 'SLIDER'
        if self.combo_index in SPINNER: return 'SPINNER'

    @property
    def combo(self):
        for i in range(4):
            if self.combo_index in [x[i] for x in HitObject.TYPE]: return i

    def is_new_combo(self):
        if self.combo_index in [x[0] for x in HitObject.TYPE]: return False
        return True

    def set_sound(self, *sounds: str):
        for sound in sounds:
            if sound not in HitObject.SOUND_ADDITION: raise ValueError
        self.sound_addition = 0
        for sound in sounds:
            self.sound_addition += HitObject.SOUND_ADDITION[sound]

    def get_sound(self):
        """ Return list(*str) """
        if self.sound_addition == 0: return None
        temp1 = self.sound_addition
        temp2 = []
        for key, val in HitObject.SOUND_ADDITION.items():
            if val == 0: return temp2
            if temp1 >= val:
                temp2.append(key)
                temp1 -= val

    def __str__(self):
        # TODO
        msg = ''
        return f'{self.x},{self.y},{self.time},{self.combo_index},{self.sound_addition},{msg}'

    # def __init__(self):
    #     self.objects = []  # list of HitObject
    # FIXME
    # def __str__(self):
    #     msg = ''
    #     for elem in self.objects:
    #         msg = msg + str(elem) + '\n'
    #     return f'[TimingPoints]\n' + msg


DEFAULT_VOLUME = 60
DEFAULT_SAMPLE = 2


class Beatmap:
    def __init__(self, fp: Path):
        assert str(fp).endswith('.osu'), 'Use this to open .osu files'
        if isinstance(fp, str):
            fp = Path(fp)
        elif isinstance(fp, Path):
            pass
        else:
            raise AttributeError('Wrong fp format!')

        with open(fp, encoding="utf8") as f:
            # assert f.readline() == f'osu file format {OSU_FILE_FORMAT}\n'

            audio_filename = read_until(f, 'AudioFilename: ')
            assert audio_filename.endswith('.mp3')
            self.audio_filepath = fp.parent / Path(audio_filename)

            self.version = read_until(f, 'Version:')
            self.AR = float(read_until(f, 'ApproachRate:'))
            read_until(f, 'TimingPoints')
            x = float(f.readline().split(',')[1])
            self.BPM = 60000 / x

            self.hit_times = []
            read_until(f, '[HitObjects]')
            current_line = f.readline()
            i = 0
            n = 250
            while i < n and current_line not in ['\n', '']:
                temp = current_line.split(',')[2]  # milliseconds str
                self.hit_times.append(round(float(temp)/1000, 3))  # seconds
                i += 1
                current_line = f.readline()


def read_until(text_file: Union[StringIO, TextIO], starting_str: str) -> str:
    """ Returns next line that begins with starting_str - starting_str """
    # TODO check and fix
    current_line = text_file.readline()
    while starting_str not in current_line and current_line != '':
        current_line = text_file.readline()
    return current_line[len(starting_str):-1]


