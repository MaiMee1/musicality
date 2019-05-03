from __future__ import annotations

from pathlib import Path
from typing import Any, Union, Optional, Tuple, List, Dict, NewType, TextIO, Iterable, Callable, Hashable
import warnings
from io import StringIO

import pyglet


class HitObject:
    """ Represents an Osu! HitObject """

    from constants import HIT_OBJECT_TYPE as TYPE, HIT_OBJECT_STATE as STATE, \
        HitObjectType as Type, HitObjectState as State

    TYPE_NAME_MAP = {
        TYPE.TAP: 'soft-hitnormal.wav',
        TYPE.HOLD: 'soft-hitwhistle.wav'
    }

    TYPE_MAXLEN_MAP = {
        TYPE.TAP: 1,
        TYPE.HOLD: 2
    }

    __slots__ = (
        '_reach_times',
        '_animation_times',
        '_symbol',
        '_type',
        '_press_times',
        '_grades',
        '_beatmap',
        '_state',
        '_cache'
    )

    def __init__(self,
                 beatmap: Beatmap,
                 time: Union[Iterable[float], float],
                 symbol: Union[Iterable[int], int],
                 note_type: Type):
        """  """
        self._reach_times, self._symbol = self._filter_input(time, symbol, note_type)
        self._press_times = []
        self._type = note_type
        self._calculate_animation_times(beatmap.BPM, beatmap.AR)
        self._beatmap = beatmap
        self._state = HitObject.STATE.INACTIVE
        self._grades = []
        self._cache = 0

    def _filter_input(self,
                      time: Union[Iterable[float], float],
                      symbol: Union[Iterable[int], int],
                      note_type: Type) -> (Iterable[float], Iterable[int]):
        """ Check and return correct input (in list) or raise AssertionError """
        error = 0
        error_msg = "'time' and 'symbol' must be of len 2 in case of HOLD note_type"
        if note_type == HitObject.TYPE.TAP:
            try:
                assert len(time) == 1, error_msg.format(1)
            except TypeError:
                time = [time]
            try:
                assert len(symbol) == 1, error_msg.format(1)
            except TypeError:
                symbol = symbol
        elif note_type == HitObject.TYPE.HOLD:
            try:
                assert len(time) == 2 and len(symbol) == 2, error_msg.format(2)
            except TypeError:
                error = 2
        else:
            raise AssertionError('wrong note_type, use constants.NOTE_TYPE')
        if error in (1, 2):
            raise AssertionError(error_msg.format(error))
        return time, symbol

    def _calculate_animation_times(self, BPM: float, AR: float):
        """ Set the _animation_times """
        assert BPM > 0
        assert 0 <= AR <= 10
        AR = AR / 3
        beat = 60 / BPM  # seconds
        delay = beat * (1 + (10 - AR) / 3)  # seconds
        self._animation_times = [reach_time - delay for reach_time in self._reach_times]  # seconds

    def press(self, time: float):
        """ Mark `time` as a press_time if pressable.
        Raise TimeoutError if not pressable """
        if self._state == HitObject.STATE.ACTIVE:
            self._press_times.append(time)
            if len(self._press_times) == HitObject.TYPE_MAXLEN_MAP[self._type]:
                self._state = HitObject.STATE.PASSED
        elif self._state == HitObject.STATE.INACTIVE:
            pass
        else:
            raise TimeoutError('object is not pressable')

    @property
    def reach_times(self) -> List[float]:
        """ Return list of times in relation to game_time (seconds)
        object needs to be interacted with by the player. """
        return self._reach_times

    def get_reach_time(self) -> float:
        """  """
        try:
            self._cache += 1
            return self._reach_times[self._cache-1]
        except IndexError:
            pass

    @property
    def reach_times_ms(self) -> List[int]:
        """ Return reach_time in milliseconds """
        return [int(time * 1000) for time in self._reach_times]

    @property
    def animation_times(self) -> List[float]:
        """ Return list of times in relation to game_time (seconds)
        graphics engine need to start animations. """
        return self._animation_times

    @property
    def animation_times_ms(self) -> List[int]:
        """ Return animation_time in milliseconds """
        return [int(time * 1000) for time in self._animation_times]

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
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol: int):
        """ Set symbol to new_symbol """
        # TODO add checking
        self._symbol = new_symbol

    @property
    def hit_sound(self) -> (int, str):
        """ Return hit_sounds of object """
        # TODO only return normal for now
        return 0, 'soft'

    @property
    def type(self) -> HitObject.Type:
        """ Return type of object """
        return self._type

    @property
    def grades(self) -> Optional[Iterable[str]]:
        """ Return grade of the object if graded. None otherwise. """
        return self._grades

    def add_grade(self, grade: str):
        # TODO add checking
        if len(self._grades) < HitObject.TYPE_MAXLEN_MAP[self._type]:
            self._grades.append(grade)
        else:
            print(f'Over maxlen, did not process {grade}')

    @property
    def state(self) -> HitObject.State:
        """ Return current state of object """
        return self._state

    def change_state(self, state: Union[str, HitObject.State]):
        if isinstance(state, str):
            self._state = {
                'active': HitObject.STATE.ACTIVE,
                'inactive': HitObject.STATE.INACTIVE,
                'passed': HitObject.STATE.PASSED
            }[state]
        else:
            self._state = state

    def _dt(self) -> List[float]:
        """ Return the time difference (seconds) between reach_time and
        press_time-- press_time - reach_time --of the instance.
        Negative if pressed early; positive if late. """
        assert self._state == HitObject.STATE.PASSED
        # TODO
        return [press - reach for press, reach in zip(self._press_times, self._reach_times)]


def get_relative_path(path: Path, relative_root: Path = Path().resolve()):
    """ Return a relative path. If already relative, return unchanged """
    from operator import truediv
    from functools import reduce
    parts = list(path.parts)
    root = relative_root.parts
    for part in parts.copy():
        if part in root:
            parts.remove(part)
    return reduce(truediv, parts, Path())


class Beatmap:
    """ Represents information from .osu + .msc files """

    def __init__(self, filepath: Path):
        """ Load information from file at path and create appropriate
        fields. """

        if filepath.is_absolute():
            filepath = get_relative_path(filepath)

        self._filepath = filepath
        self._loader = pyglet.resource.Loader([str(self.get_folder_path(absolute=True)), '.'])

        if filepath.suffix == '.msc':
            raise NotImplementedError('.msc files not implemented yet')
        assert filepath.suffix == '.osu', 'only use this to open .osu files'

        # custom sample override
        from constants import SAMPLE_NAMES
        wav_files = filepath.glob('*.wav')
        self._sample_filenames = [file.name for file in wav_files
                                  if file.name in (name + '.wav' for name in SAMPLE_NAMES)]

        # load info from .osu
        def read_until(text_file: Union[StringIO, TextIO], starting_str: str) -> str:
            """ Returns next line that begins with starting_str - starting_str """
            # TODO add checking and fix not in current to sth
            current = text_file.readline()
            while starting_str not in current and current != '':
                current = text_file.readline()
            return current[len(starting_str):-1]

        with open(filepath, encoding="utf8") as f:
            # TODO check if it really works for every version
            first_line = f.readline()
            if first_line not in [f"osu file format v{x}\n" for x in (14, 13, 12)]:
                warnings.warn(f"reading beatmap file... osu file format version '{first_line[-4:-1]}' is not known", ResourceWarning)

            audio_filename = read_until(f, 'AudioFilename: ')
            assert audio_filename.endswith('.mp3')
            self._audio_filepath = filepath.parent / Path(audio_filename)

            def get_data(container: Dict,
                         str_heads: Iterable[str],
                         keys: Optional[Iterable[str]] = None,
                         to_int: Optional[Iterable[str], str] = None,
                         to_float: Optional[Iterable[str], str] = None,
                         **kwargs):
                """ Read into container. Mutates container. Custom for v14, 12 only """
                if to_int:
                    kwargs['to_int'] = int, to_int
                if to_float:
                    kwargs['to_float'] = float, to_float

                func_map = {}
                for k, v in kwargs.items():
                    assert len(v) == 2
                    # type: Tuple[Callable[[str], Any], Union[Iterable[str], str]]
                    if v[1] == 'all':
                        func_map['all'] = v[0], k
                    else:
                        for elem in v[1]:
                            func_map[elem] = v[0], k

                if keys is None:
                    # if keys is not specified only use strings before ':'
                    keys = [str_head.split(':')[0] for str_head in str_heads]

                for str_head, key in zip(str_heads, keys):
                    value = read_until(f, str_head)
                    try:
                        if 'all' in func_map.keys():
                            value = func_map['all'][0](value)
                        elif key in func_map:
                            value = func_map[key][0](value)
                    except TypeError:
                        operation = ' '.join(func_map[key][1].split('_'))
                        warnings.warn(f"reading .osu file... failed to convert '{value}' {operation}")
                    except ValueError as e:
                        print(value, func_map['all'][0])
                        raise e
                    container[key] = value

            self._metadata = {}
            get_data(self._metadata,
                     ('Title:','TitleUnicode:', 'ArtistUnicode:', 'Creator:',
                      'Version:', 'Source:', 'Tags:', 'BeatmapID:', 'BeatmapSetID:'),
                     to_int=['BeatmapID', 'BeatmapSetID'],
                     to_list=(lambda s: [x for x in s.split(' ')], ('Tags',)))

            self._difficulty = {}
            get_data(self._difficulty,
                     ('HPDrainRate:', 'CircleSize:', 'OverallDifficulty:', 'ApproachRate:',
                      'SliderMultiplier:', 'SliderTickRate:'),
                     to_float='all')

            self._background_filename, self._video_filename = None, None
            read_until(f, '//Background and Video events')
            l = None
            while l != '//Break Periods\n':
                l = f.readline()
                for elem in l.split('"'):
                    if elem.endswith('.jpg'):
                        self._background_filename = elem
                    elif elem.endswith('.png'):
                        self._background_filename = elem
                    elif elem.endswith('.mp4'):
                        self._video_filename = elem
                    elif elem.endswith('.avi'):
                        self._video_filename = elem
                    else:
                        warnings.warn(f"reading .osu file... unknown file format: '{elem}'", ResourceWarning)

            # TODO get average BPM instead
            read_until(f, '[TimingPoints]')
            x = float(f.readline().split(',')[1])
            self._BPM = 60000 / x

            self._hit_times = []
            read_until(f, '[HitObjects]')
            current_line = f.readline()
            i = 0
            n = 3000
            while i < n and current_line not in ['\n', '']:
                temp = current_line.split(',')[2]  # milliseconds str
                self._hit_times.append(round(float(temp)/1000, 3))  # seconds
                i += 1
                current_line = f.readline()

    def __str__(self):
        return self._filepath.name[:-4]

    @property
    def resource_loader(self):
        """ Return resource loader of folder of beatmap file """
        return self._loader

    def get_folder_path(self, absolute=False) -> Path:
        """ Return folder path of the instance """
        if absolute:
            return Path().resolve() / self._filepath.parent
        return self._filepath.parent

    @property
    def audio_filename(self) -> str:
        """ Return name of the song file """
        return self._audio_filepath.name

    @property
    def background_filename(self) -> Optional[str]:
        """ Return name of the song file """
        if self._background_filename:
            return self._background_filename

    @property
    def video_filename(self) -> Optional[str]:
        """ Return name of the video file """
        return self._video_filename

    def background_image(self) -> Optional[pyglet.image.AbstractImage]:
        """ Generate and return an image that can be drawn """
        if self._background_filename:
            return self._loader.image(self._background_filename)

    def get_samples_filenames(self) -> List[str]:
        """ Return name of the custom sample that exists """
        filenames = []
        for name, path in self._sample_filenames.items():
            try:
                path.relative_to(Path().resolve())
                filenames.append(name)
            except ValueError:
                pass
        return filenames

    def generate_audio(self) -> Audio:
        """ Generate and return an audio player object """
        return Audio(filename=self.audio_filename, loader=self._loader)

    def generate_hit_sounds(self) -> List[Audio]:
        """ Generate and return a list of audio objects """
        temp = [Audio(filename=name, loader=self._loader) for name in self._sample_filenames]
        return temp

    def generate_video(self) -> Optional[pyglet.media.Source]:
        """ Generate and return a video that can be played, played, paused, replayed
        , and set time. """
        if self.video_filename:
            return self._loader.media(self.video_filename)

    def generate_hit_objects(self) -> List[HitObject]:
        """ Generate and return a list of processed hit_objects """
        from random import choice, seed, shuffle
        import key

        seed(round(sum(self._hit_times), 3))

        def get_random(L: list, cache=[]):
            if not cache:
                shuffle(L)
                cache.extend(L[:5])
            return cache.pop(-1)

        hit_objects = [
            HitObject(self, hit_time, get_random(key.normal_keys), HitObject.TYPE.TAP)
            for hit_time in self._hit_times
        ]
        return hit_objects

    @property
    def version(self) -> str:
        """ Return the version-- difficulty --of the instance """
        return self._metadata['Version']

    @property
    def BPM(self) -> float:
        """ Return the BPM-- beats per minute --of the instance """
        return self._BPM

    @property
    def HP(self) -> float:
        """ Return the HP drain rate of the instance """
        return self._difficulty['HPDrainRate']

    @property
    def OD(self) -> float:
        """ Return the overall difficulty of the instance """
        return self._difficulty['OverallDifficulty']

    @property
    def AR(self) -> float:
        """ Return the approach rate of the instance """
        return self._difficulty['ApproachRate']


# helper class
class Time:
    """ Represents time """

    __slots__ = '_time'

    def __init__(self, time: Union[str, int, float]):
        """ Assume time is either (1) in seconds or (2) a string in the
        correct format. """
        try:
            time > 0
            # Doesn't raise error if time is a number
            self._time = float(time)
        except TypeError:
            # Assume new_time is str
            h_str, m_str, ms_str = 0, 0, 0
            if '.' in time:
                try:
                    time, ms_str = time.split('.')
                except ValueError:
                    try:
                        m_str, time, ms_str = time.split('.')
                    except ValueError:
                        h_str, m_str, time, ms_str = time.split('.')
                    except:
                        raise ValueError("invalid format for 'time'")
            if ':' in time:
                try:
                    m_str, time = time.split(':')
                except ValueError:
                    h_str, m_str, time = time.split(':')
                except:
                    raise ValueError("invalid format for 'time'")
            self._time = int(h_str) * 3600 + int(m_str) * 60 + int(time) + int(ms_str) / 1000
            round(self._time, 10)

    def __str__(self):
        """ Return string in the format hh:mm:ss.ms """
        ms = (self._time % 1) * 1000
        s = self._time % 60
        m = (self._time // 60) % 60
        h = self._time // 3600
        return f'{h:02.0f}:{m:02.0f}:{s:02.0f}.{ms:.0f}'

    def __float__(self):
        """ Return time in seconds """
        return self._time

    def __int__(self):
        """ Return time in milliseconds """
        return int(self._time * 1000)

    def __add__(self, other: Union[str, int, float]) -> Time:
        """ Allows other to be  """
        if type(other) in (str, int):
            other = Time(other)
        return Time(float(self) + float(other))

    def __sub__(self, other: Union[str, int, float]) -> Time:
        """  """
        if type(other) in (str, int):
            other = Time(other)
        return Time(float(self) - float(other))


# helper class
class Audio:
    """ Represents audio file """

    __slots__ = '_source', '_player', '_filename', '_constructor'

    def __init__(self, *,
                 filepath: Path = None, absolute: bool = False,
                 filename: str = '', loader: pyglet.resource.Loader = None,
                 **kwargs):
        """ Load audio file from (1) filepath or (2) filename using a loader.
        Assume arguments are in the correct type. """
        from functools import partial
        constructor = kwargs.pop('constructor', None)
        if constructor:
            self._constructor = constructor
            assert filename != ''
            self._filename = filename
        elif loader:
            if filename:
                if filepath:
                    assert filepath.name == filename
            else:
                if filepath:
                    filename = filepath.name
                else:
                    raise TypeError("Audio() needs 'filename' if 'loader' is used and 'filepath' is not specified")
            self._filename = filename
        else:
            if filepath:
                if absolute:
                    raise AssertionError
                loader = pyglet.resource.Loader([filepath.parent])
                self._filename = filepath.name
            else:
                raise TypeError("Audio() missing 1 required keyword argument: 'filepath'")
        self._constructor = partial(loader.media, name=self._filename)
        self._source = self._constructor()
        self._player = pyglet.media.Player()
        self._player.queue(self._source)

    @property
    def name(self):
        """ Return the filename of the audio """
        return self._filename

    @property
    def source(self):
        """ Return the source of this audio """
        return self._source

    @property
    def duration(self):
        """ Return length of the audio (seconds) """
        return self._source.duration

    def play(self):
        """
        Begin playing the current source.

        This has no effect if the player is already playing.
        """
        assert not self.playing
        if self._player.source is None:
            self._player.queue(self._source)
        self._player.play()

    def stop(self):
        """ Stop the audio if playing """
        self._player.pause()
        self._player.seek(0)

    @property
    def playing(self) -> bool:
        """ Return True if audio is playing, False otherwise """
        return self._player.playing

    def pause(self):
        """ Pause the audio """
        self._player.pause()

    @property
    def time(self):
        """ Return current time of the audio (seconds) """
        return self._player.time

    @time.setter
    def time(self, time: Union[str, int, float]):
        """ Set current time to new_time"""
        time = Time(time)
        self._player.seek(float(time))

    @property
    def player(self) -> Optional[pyglet.media.Player]:
        """ Return the player of this audio """
        return self._player

    @property
    def volume(self) -> float:
        """ Return the volume of this audio"""
        return self._player.volume

    @volume.setter
    def volume(self, new_value: float):
        """ Return the volume of this audio"""
        self._player.volume = new_value

    def clone(self) -> Audio:
        """ Returns a new instance identical to self. """
        temp = Audio(filename=self._filename, constructor=self._constructor)
        return temp


class AudioEngine:
    """ Manages audio """

    __slots__ = '_beatmap', '_sample_sets', '_song', '_audios', '_players', '_default_loader'

    from constants import SAMPLE_NAMES, HIT_SOUND_MAP, SAMPLE_SET

    def __init__(self):
        self._sample_sets = []  # type: List[Dict[str, Audio]]
        self._default_loader = pyglet.resource.Loader(['resources/Default/sample', 'resources/Default'])
        self._audios = []  # type: List[Audio]

    def load_beatmap(self, beatmap: Beatmap):
        """ Call this each game """
        self._beatmap = beatmap
        self._song = Audio(filename=beatmap.audio_filename, loader=beatmap.resource_loader)
        self.register(self._song)

    def _generate_sample_set(self):
        d = {audio.name[:-4]: audio for audio in self._beatmap.generate_hit_sounds()}
        for name in AudioEngine.SAMPLE_NAMES:
            if name not in d:
                audio = Audio(filename=(name + '.wav'), loader=self._default_loader)
                self.register(audio)
                d[name] = audio
        assert d != {}
        self._sample_sets.append(d)

    def _load_default(self, sample: str) -> Audio:
        """ Load sample from default sample """
        if sample not in AudioEngine.SAMPLE_NAMES:
            pass
        audio = Audio(filepath=Path('resources/Default/sample/' + sample + '.wav'))
        return audio

    def register(self, *audios: Audio):
        """ Register the audio file the let audio engine handle it """
        self._audios.extend(audios)

    def play_sound(self, hit_sound: int, sample_set: str):
        """ Play hit_sound according to code given """
        assert hit_sound in AudioEngine.HIT_SOUND_MAP.keys()
        assert sample_set in AudioEngine.SAMPLE_SET

        for sample in AudioEngine.HIT_SOUND_MAP[hit_sound]:
            name = sample_set + '-' + sample
            for sample_dict in self._sample_sets:
                if sample_dict[name].playing:
                    continue
                else:
                    sample_dict[name].play()
                    break
            else:
                self._generate_sample_set()
                self._sample_sets[-1][name].play()

    @property
    def song(self) -> Audio:
        """ Return the song """
        return self._song
