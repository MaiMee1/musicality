from __future__ import annotations

from pathlib import Path
from io import StringIO
from typing import Any, Union, Optional, Tuple, List, Dict, NewType, TextIO, Iterable, Callable
import warnings

import arcade
import pyglet
# TODO how to play


class TimeEngine:
    """ Manages time """

    __slots__ = 'time', '_frame_times', '_t', '_start_time', '_dt'

    def __init__(self, maxlen: int = 60):
        import time
        import collections
        self.time = time.perf_counter
        self._frame_times = collections.deque(maxlen=maxlen)
        # Ensure that deque is not empty and sum() != 0
        self._t = self._start_time = self.time()
        self._dt = 0
        self.tick()

    def tick(self):
        """ Call to signify one frame passing """
        t = self.time()
        self._dt = dt = t - self._t
        self._t = t
        self._frame_times.append(dt)

    @property
    def fps(self) -> float:
        """ Return current average fps """
        return len(self._frame_times) / sum(self._frame_times)

    @property
    def game_time(self) -> float:
        """ Return current time at function call in seconds """
        return self.time() - self._start_time

    @property
    def dt(self) -> float:
        """ Return time difference of this and last frame in seconds """
        return self._dt

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
            self._time = int(h_str)*3600 + int(m_str)*60 + int(time) + int(ms_str)/1000
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

    __slots__ = '_source', '_engine'

    def __init__(self, *,
                 filepath: Path = None, absolute: bool = False,
                 filename: str = '', loader: pyglet.resource.Loader = None):
        """ Load audio file from (1) filepath or (2) filename using a loader.
        Assume arguments are in the correct type. """
        if loader:
            if filename:
                if filepath:
                    assert filepath.name == filename
            else:
                if filepath:
                    filename = filepath.name
                else:
                    raise TypeError("Audio() needs 'filename' if 'loader' is used and 'filepath' is not specified")
            self._source = loader.media(filename)
        else:
            if filepath:
                if not absolute:
                    filepath = Path().resolve() / filepath
                pyglet.resource.path.append(filepath.parent)
                pyglet.resource.reindex()
                self._source = pyglet.media.load(filepath.name)
            else:
                raise TypeError("Audio() missing 1 required keyword argument: 'filepath'")
        self._engine = None  # type: AudioEngine

    @property
    def duration(self):
        """ Return length of the audio """
        return self._source.duration

    def set_engine(self, engine: AudioEngine):
        """ Set audio handler to `engine` """
        self._engine = engine

    def play(self):
        """ Play the audio """
        try:
            self._engine.play(self)
        except AttributeError:
            self._source.play()

    # Need to bind with an engine before callable

    def stop(self):
        """ Stop the audio if playing """
        self._engine.pause(self)
        self._engine.seek(self, 0)

    @property
    def playing(self) -> bool:
        """ Return True if audio is playing, False otherwise """
        return self._engine.playing(self)

    def pause(self):
        """ Pause the audio """
        self._engine.pause(self)

    @property
    def time(self):
        """ Return current time of the audio (seconds) """
        return self._engine.time(self)

    @time.setter
    def time(self, new_time: Union[str, int, float]):
        """ Set current time to new_time"""
        new_time = Time(new_time)
        self._engine.seek(self, float(new_time))


class AudioEngine:
    """ Manages audio """
    def __init__(self, beatmap: Beatmap, time_engine: TimeEngine):
        self._audios = []  # type: List[Audio]

    # def load_song(self, song_path: Optional[Path]):
    #     """ Get things going. (Re)Load file from path and initialize
    #     for playing. Set game_time to zero - wait_time. """
    #     pass

    def register(self, *audios: Audio):
        """ Register the audio file the let audio engine handle it """
        for audio in audios:
            audio.set_engine(self)
        self._audios.extend(audios)

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

    from constants import SAMPLE_NAMES

    def __init__(self, filepath: Path):
        """ Load information from file at path and create appropriate
        fields. """

        if filepath.is_absolute():
            filepath = get_relative_path(filepath)

        self._filepath = filepath
        self._loader = pyglet.resource.Loader([self.get_folder_path(absolute=True), '.'])

        if filepath.suffix == '.msc':
            raise NotImplementedError('.msc files not implemented yet')
        assert filepath.suffix == '.osu', 'only use this to open .osu files'

        # load default samples
        self._sample = {file.name:file.resolve()
                        for file in Path('resources/Default/sample').iterdir()}  # type: Dict[str, Path]
        # custom sample override
        wav_files = filepath.glob('*.wav')
        for file in wav_files:
            if file.name in (name for name in self._sample.keys()):
                self._sample[file.name] = file.resolve()

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
                    v # type: Tuple[Callable[[str], Any], Union[Iterable[str], str]]
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
                    container[key] = value

            self._metadata = {}
            get_data(self._metadata,
                     ('Title:','TitleUnicode:', 'ArtistUnicode:', 'Creator:',
                      'Version:', 'Source:', 'Tags:', 'BeatmapID:', 'BeatmapSetID:'),
                     to_int=['BeatmapID', 'BeatmapSetID'],
                     to_list=(lambda s: [x for x in s.split(' ')], ('Tags',)))

            self._difficulty = {}
            get_data(self._difficulty,
                     ('HPDrainRate:','CircleSize::', 'OverallDifficulty:', 'ApproachRate:',
                      'SliderMultiplier:', 'SliderTickRate:'),
                     to_float='all')

            self._background_filename, self._video_filename = None, None
            read_until(f, '//Background and Video events')
            l = None
            while l != '//Break Periods':
                l = f.readline()
                for elem in l.split('"'):
                    try:
                        {'.jpg': self._background_filename,
                         '.png': self._background_filename,
                         '.mp4': self._video_filename,
                         '.avi': self._video_filename,
                         }[elem] = l
                    except KeyError:
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


    def get_folder_path(self, absolute=False) -> Path:
        """ Return folder path of the instance """
        if absolute:
            return Path().resolve() / self._filepath.parent
        return self._filepath.parent

    def get_audio_path(self, absolute=False) -> Path:
        """ Return path to the audio file-- the song (mostly .mp3) --of
        the instance. """
        if absolute:
            return Path().resolve() / self._audio_filepath
        return  self._audio_filepath

    @property
    def audio_filename(self) -> str:
        """ Return name of the audio file """
        return self._audio_filepath.name

    @property
    def audio(self) -> Audio:
        """ Generate and return an audio object """
        return Audio(filename=self.audio_filename, loader=self._loader)

    def get_hit_sound_paths(self, absolute=False) -> List[Path]:
        """ Return a list of paths to hit_sounds-- sounds a keypress
        maps to (mostly .wav) --files of the instance. """
        pass

    @property
    def hit_sound_filenames(self) -> List[str]:
        """ Return names of the hit_sound files in the song's directory """
        filenames = []
        for name, path in self._sample.items():
            try:
                path.relative_to(Path().resolve())
                filenames.append(name)
            except ValueError:
                pass
        return filenames

    def hit_sounds(self) -> List[Audio]:
        """ Generate and return a list of audio objects """
        return [Audio(filepath=path) for path in self._sample.values()]

    def get_hit_sound(self, name: str) -> Audio:
        """ Generate and return an audio object """
        assert name in Beatmap.SAMPLE_NAMES
        return Audio(filepath=self._sample[name])

    def get_background_path(self, absolute=False) -> Optional[Path]:
        """ Return path to background image(s?) of the instance """
        if self._background_filename is None:
            return None
        if absolute:
            return self.get_folder_path(absolute=True) / self._background_filename
        return self.get_folder_path() / self._background_filename

    @property
    def background_filename(self) -> Optional[str]:
        """ Return name of the background image file """
        if self._background_filename is None:
            return self._background_filename

    def background_image(self) -> pyglet.image.AbstractImage:
        """ Generate and return an image that can be drawn """
        pass

    def get_video_path(self, absolute=False) -> Optional[Path]:
        """ Return path to video of the instance """
        if self._video_filename is None:
            return None
        if absolute:
            return self.get_folder_path(absolute=True) / self._video_filename
        return self.get_folder_path() / self._video_filename

    @property
    def video_filename(self) -> Optional[str]:
        """ Return name of the video file """
        if self._video_filename is None:
            return None
        return self._video_filename

    def video(self) -> pyglet.media.Source:
        """ Generate and return a video that can be played, played, paused, replayed
        , and set time. """
        pass

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

    def hit_objects(self) -> List[HitObject]:
        """ Return a list of processed hit_objects of the instance """
        pass


class HitObject:
    """ Represents an Osu! HitObject """

    from constants import HIT_OBJECT_TYPES as TYPE, HIT_OBJECT_STATES as STATE, \
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
        '_start_times',
        '_symbol',
        '_type',
        '_hit_sound',
        '_press_times',
        '_beatmap',
        '_state',
        '_combo'
    )

    def __init__(self,
                 beatmap: Beatmap,
                 time: Union[Iterable[float], float],
                 symbol: Union[Iterable[int], int],
                 note_type: Type):
        """  """
        self._reach_times, self._symbol = self._filter_input(time, symbol, note_type)
        self._type = note_type
        self._hit_sound = beatmap.get_hit_sound(HitObject.TYPE_NAME_MAP[note_type])
        self._calculate_start_time(beatmap.BPM, beatmap.AR)
        self._beatmap = beatmap
        self._state = HitObject.STATE.INACTIVE
        self._combo = None

    def _filter_input(self,
                      time: Union[Iterable[float], float],
                      symbol: Union[Iterable[int], int],
                      note_type: Type) -> (Iterable[float], Iterable[int]):
        """ Check and return correct input or raise AssertionError """
        error = 0
        error_msg = "'time' and 'symbol' must be of len {} in case of HOLD note_type"
        if note_type == HitObject.TYPE.TAP:
            try:
                assert len(time) == 1, error_msg.format(1)
            except TypeError:
                time = [time]
            try:
                assert len(symbol) == 1, error_msg.format(1)
            except TypeError:
                symbol = [symbol]
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

    def _calculate_start_time(self, BPM: float, AR: float):
        """ Set the start_time"""
        assert BPM > 0
        assert 0 <= AR <= 10
        AR = AR / 2
        beat = 60 / BPM  # seconds
        delay = beat * (1 + (10 - AR) / 3)  # seconds
        self._start_times = [reach_time - delay for reach_time in self._reach_times]  # seconds

    @property
    def reach_time(self) -> float:
        """ Return the time (seconds) in relation to game_time the
        instance need to be hit. """
        return self._reach_times[0]

    @property
    def reach_time_ms(self) -> int:
        """ Return the time (milliseconds) in relation to game_time the
        instance need to be hit. """
        return int(self._reach_times[0] * 1000)

    @property
    def start_time(self) -> float:
        """ Return the time (seconds) in relation to game_time the
        instance need to start coming in. """
        return self._start_times[0]

    @property
    def start_time_ms(self) -> int:
        """ Return the time (milliseconds) in relation to game_time the
        instance need to coming in. """
        return int(self._start_times[0] * 1000)

    @property
    def stop_time(self) -> float:
        """ Return the time (seconds) in relation to game_time the
        instance need to stop coming in. """
        return self._start_times[1]

    @property
    def stop_time_ms(self) -> int:
        """ Return the time (milliseconds) in relation to game_time the
        instance need to stop coming in. """
        return int(self._start_times[1] * 1000)

    @property
    def symbol(self) -> int:
        """ Return the symbol of the key the instance need to come in """
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol: int):
        """ Set symbol to new_symbol """
        # TODO add checking
        self._symbol = new_symbol

    def sound(self) -> Audio:
        """ Play hit_sound """
        return self._hit_sound.play()

    @property
    def state(self) -> HitObject.Type:
        """ Return the current state of the instance """
        return self._type

    @property
    def grade(self) -> Optional[str]:
        """ Return the grade of the instance if gradable.
        None otherwise. """
        if self._type != HitObject.STATE.PASSED:
            return
        grade = 'Perfect'  # TODO FIND A RUBRIC
        if grade in ('Bad', 'Good', 'Perfect'):
            self._combo += 1
        return grade

    def press(self, time: float, current_combo: int):
        """ Mark `time` as a press time if pressable.
        Return grade if gradable. Raise TimeoutError if not pressable """
        if self.state == HitObject.STATE.ACTIVE:
            self._press_times.append(time)
            self._combo = current_combo
        else:
            raise TimeoutError('object is not pressable')
        if len(self._press_times) == HitObject.TYPE_MAXLEN_MAP[self._type]:
            self._state = HitObject.STATE.PASSED

    def _dt(self) -> List[float]:
        """ Return the time difference (seconds) between reach_time and
        press_time-- press_time - reach_time --of the instance.
        Negative if pressed early; positive if late. """
        assert self._state == HitObject.STATE.PASSED
        # TODO
        return [press - reach for press, reach in zip(self._press_times, self._reach_times)]

    def _cal_accuracy(self, dt: float) -> float:
        """ Calculate accuracy of given dt """
        pass  # TODO FIND A RUBRIC

    @property
    def accuracy(self) -> Optional[float]:
        """ Return the accuracy of the instance if gradable.
        None otherwise. """
        pass  # TODO FIND A RUBRIC

    @property
    def combo(self) -> Optional[int]:
        """ Return combo at the time the instance was hit. Include the
        instance in the calculation as well. """
        if self._combo is not None:
            return self._combo


class Key:
    """ Represents a key on the virtual keyboard """
    def __init__(self):
        self._hit_object: HitObject = HitObject()

    @property
    def hit_object(self) -> Optional[HitObject]:
        """ """
        if self._hit_object:
            return self._hit_object

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

    def press(self):
        """ Play appropriate graphics for pressing key """
        pass

    def release(self):
        """ Play appropriate graphics for releasing key """
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


class KeyboardModel:
    """ Data collection for different keyboard types """
    def __int__(self):
        self._size: float
        self._height: float
        self._keys: dict


class Keyboard:
    """ Represents the board behind keys """
    def __init__(self):
        self.keys: Dict[int, Key] = {}

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


class Clock:
    """ Represents on-screen clock showing game progress """
    def __init__(self, time_engine: TimeEngine, beatmap: Beatmap):
        self._time_engine = time_engine
        self._time = 0
        self._duration = beatmap.audio.duration
        pass

    def update(self):
        """ Update the element """
        self._time = self._time_engine.game_time

    def draw(self):
        """ Draw the element """
        ratio = self._time / self._duration
        # TODO make a draw function


class Score:
    """ Represents on-screen score """
    def __init__(self):
        self._score = 0
        pass

    def update(self):
        """ Update the element's graphic component to match data """
        pass

    def draw(self):
        """ Draw the graphical representation of the element """
        pass

    @property
    def score(self):
        """ Return current score """
        return self._score

    def __iadd__(self, other: int):
        """ Add the current score by `other` """
        self._score += other


class Combo:
    """ Represents on-screen combo """
    def __init__(self):
        self._combo = [0]  # type: List[int]

    def update(self):
        """ Update the element's graphic component to match data """
        pass

    def draw(self):
        """ Draw the graphical representation of the element """
        pass

    @property
    def combo(self) -> int:
        """ Return current combo """
        return self._combo[-1]

    def break_(self):
        """ Break the current combo """
        self._combo.append(0)

    def __iadd__(self, other: int):
        """ Add to the current combo by `other` """
        self._combo[-1] += other


class AccuracyBar:
    """ Represents on-screen accuracy bar """
    DEFAULT_LEN = 10

    def __init__(self):
        from collections import deque
        self._stack = deque(maxlen=AccuracyBar.DEFAULT_LEN)

    def update(self):
        """ Update the element's graphic component to match data """
        pass

    def draw(self):
        """ Draw the graphical representation of the element """
        pass

    def average_accuracy(self):
        """ Return current average accuracy """
        return sum(self._stack) / len(self._stack)

    def stack_len(self):
        """ Return the number of last hit_objects used to calculate
        average_accuracy and shown on-screen. """
        return self._stack.maxlen

    def set_stack_len(self, new_len: int):
        """ Change stack_len to new_len """
        from collections import deque
        old = self._stack
        self._stack = deque(maxlen=new_len)
        self._stack.extend(old)

    def __iadd__(self, other: float):
        """ Add new accuracy to bar """
        self._stack.append(other)


class Game:
    """ """
    from constants import GameState as State, GAME_STATE as STATE

    def __int__(self, song: str, difficulty: str):
        filepath = self.get_beatmap_filepath(song, difficulty)
        if filepath is None:
            print('loading song... failed to get filepath')
            a = input('specify filepath? (Y/N)')
            while a not in 'YNyn':
                a = input('specify filepath? (Y/N)')
            if a in 'Yy':
                filepath = a
            else:
                quit()

        self.time_engine = TimeEngine()
        self.audio_engine = AudioEngine()
        self.beatmap = Beatmap(filepath)
        self.keyboard = Keyboard()
        self.clock = Clock(self.time_engine, self.beatmap)
        self.score = Score()
        self.combo = Combo()
        self.accuracy_bar = AccuracyBar()

        self.hit_objects = self.beatmap.hit_objects()
        self._state = Game.STATE.GAME_PLAYING
        self._update_rate = 1/60

    def update(self, delta_time: float):
        self.keyboard.update()

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        """ This is called during the idle time when it should be called """
        self.time_engine.tick()
        self.keyboard.draw()
        self.clock.draw()
        self.score.draw()
        self.combo.draw()
        self.accuracy_bar.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        try:
            key = self.keyboard.keys[symbol]
        except KeyError:
            key = None
        if key:
            time = self.time_engine.game_time
            key.press()
            hit_object = key.hit_object
            if hit_object:
                hit_object.press(time, self.combo.combo)
                if hit_object.combo > self.combo.combo:
                    pass
                else:
                    self.combo.break_()
                self.combo += hit_object.new_combo - self.combo.combo
                self.accuracy_bar += hit_object.accuracy
                self.score += hit_object.new_score


    def on_key_release(self, symbol: int, modifiers: int):
        try:
            key = self.keyboard.keys[symbol]
        except KeyError:
            key = None
        if key:
            time = self.time_engine.game_time
            key.release()
            key.press()
            hit_object = key.hit_object
            if hit_object:
                hit_object.press(time, self.combo.combo)
                if hit_object.combo > self.combo.combo:
                    pass
                else:
                    self.combo.break_()
                self.combo += hit_object.combo - self.combo.combo
                self.accuracy_bar += hit_object.accuracy
                self.score += hit_object.score

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
        self.keyboard.set_update_rate(rate)
        self._update_rate = rate

    @property
    def state(self):
        """ Return current state of the instance """
        return self._state

    def get_beatmap_filepath(self, song: str, difficulty: str) -> Path:
        """ Return the filepath to .osu file given the name and
        difficulty of the song. """
        songs = Path('resources/Songs').rglob(f'*{song}')
        try:
            song = songs.__next__()
            return song
        except StopIteration:
            return None


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