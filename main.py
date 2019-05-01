from __future__ import annotations

from pathlib import Path
from io import StringIO
from typing import Any, Union, Optional, Tuple, List, Dict, NewType, TextIO, Iterable, Callable, Hashable
import warnings
from random import random

import arcade
import pyglet

import key as key_
from keyboard import Keyboard, Key, Rectangle
import keyboard as keyboard_
# TODO how to play


class TimeEngine:
    """ Manages time """

    __slots__ = 'time', '_frame_times', '_t', '_start_time', '_dt', '_start', '_audio_engine'

    def __init__(self, maxlen: int = 60):
        import time
        import collections
        self.time = time.perf_counter
        self._frame_times = collections.deque(maxlen=maxlen)
        # Ensure that deque is not empty and sum() != 0
        self._t = self._start_time = self.time()
        self._dt = 0
        self.tick()
        self._start = False

    def init_engine(self, game: Game):
        """ Maneuvering circular dependency """
        self._audio_engine = game._audio_engine

    def tick(self):
        """ Call to signify one frame passing """
        t = self.time()
        self._dt = dt = t - self._t
        self._t = t
        self._frame_times.append(dt)

    def start(self):
        """ Start the clock """
        self._start = True
        self._start_time = self.time()

    def reset(self):
        """ Restart the clock """
        self._start_time = self.time()

    @property
    def fps(self) -> float:
        """ Return current average fps """
        try:
            return len(self._frame_times) / sum(self._frame_times)
        except ZeroDivisionError:
            return 0

    @property
    def game_time(self) -> float:
        """ Return current time at function call in seconds """
        try:
            assert self._start
            time = self.time()
            audio_time = self._audio_engine.song.time
            diff = audio_time - time
            if diff:
                time += diff / 2
            return self.time() - self._start_time
        except AssertionError:
            return 0

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

    __slots__ = '_source', '_player', '_filename', '_engine', '_constructor'

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

        self._engine: AudioEngine

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

    def set_engine(self, engine: AudioEngine):
        """ Set audio handler to `engine` """
        self._engine = engine

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
    
    def clone(self) -> Audio:
        """ Returns a new instance identical to self. """
        temp = Audio(filename=self._filename, constructor=self._constructor)
        try:
            temp.set_engine(self._engine)
        except AttributeError:
            pass
        return temp


class AudioEngine:
    """ Manages audio """

    __slots__ = '_beatmap', '_sample_sets', '_song', '_audios', '_players', '_default_loader'

    from constants import SAMPLE_NAMES, HIT_SOUND_MAP, SAMPLE_SET

    def __init__(self, beatmap: Beatmap):
        self._beatmap = beatmap
        self._sample_sets = []  # type: List[Dict[str, Audio]]
        self._default_loader = pyglet.resource.Loader(['resources/Default/sample', 'resources/Default'])

        self._song = Audio(filename=beatmap.audio_filename, loader=beatmap.resource_loader)

        self._audios = []  # type: List[Audio]

        self.register(self._song)
        self._generate_sample_set()

    def init_engine(self, game: Game):
        """ Maneuvering circular dependency """
        pass

    # def load_song(self, song_path: Optional[Path]):
    #     """ Get things going. (Re)Load file from path and initialize
    #     for playing. Set game_time to zero - wait_time. """
    #     pass

    def _generate_sample_set(self):
        d = {audio.name[:-4]: audio for audio in self._beatmap.generate_hit_sounds()}
        for name in AudioEngine.SAMPLE_NAMES:
            if name not in d:
                audio = Audio(filename=(name+'.wav'), loader=self._default_loader)
                self.register(audio)
                d[name] = audio
        assert d != {}
        self._sample_sets.append(d)

    def _load_default(self, sample: str) -> Audio:
        """ Load sample from default sample """
        if sample not in AudioEngine.SAMPLE_NAMES:
            pass
        audio = Audio(filepath=Path('resources/Default/sample/'+sample+'.wav'))
        return audio

    def register(self, *audios: Audio):
        """ Register the audio file the let audio engine handle it """
        for audio in audios:
            audio.set_engine(self)
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


class ScoreEngine:
    """ Manages calculation of score, combo, grade, etc. """
    def __init__(self, beatmap: Beatmap):
        from collections import deque
        self.beatmap = beatmap
        self._score = 0
        self._combo = [0]
        self._perfect = True
        self._not_missed = True
        self._accuracy_stack = deque(maxlen=20)
        self._grade_stack = []

    def init_engine(self, game: Game):
        """ Maneuvering circular dependency """
        pass

    def register_hit(self, hit_object: HitObject, time: float, type: HitObject.Type):
        """ `time` = -1 for misses """
        # TODO
        accuracy = self._calculate_accuracy(time)
        grade = self._calculate_grade(accuracy)
        score = self._calculate_score(grade, type)

        if time == -1:
            grade = 'miss'
            score = 0

        self._accuracy_stack.append(accuracy)
        self._grade_stack.append(abs(1-accuracy))
        if self._perfect:
            if grade != 'perfect':
                self._perfect = False
        if grade == 'miss':
            self._break_combo()
            if self._not_missed:
                self._not_missed = False
        else:
            self._combo[-1] += 1
        hit_object.add_grade(grade)
        self._score += score

    def _calculate_accuracy(self, time: float) -> float:
        # TODO
        return 0

    def _calculate_grade(self, accuracy: float) -> str:
        # TODO
        return 'perfect'

    def _calculate_score(self, grade: str, type: HitObject.Type):
        # TODO
        return 300

    @property
    def score(self) -> int:
        """ Returns current score """
        return self._score

    @property
    def combo(self) -> int:
        """ Returns current combo """
        return self._combo[-1]

    def _break_combo(self):
        self._combo.append(0)

    @property
    def overall_grade(self) -> str:
        """ Returns current overall grade """
        if self._perfect:
            return 'SS'
        if self._not_missed:
            return 'S'
        # TODO
        return 'A'

    @property
    def overall_accuracy(self) -> float:
        """ Returns current overall accuracy in percent """
        return sum(self._grade_stack) / len(self._grade_stack)

    @property
    def current_accuracies(self) -> Iterable[float]:
        """ Returns current accuracies in accuracy """
        return self._accuracy_stack


class FX:
    """ Represents a graphical fx """
    def __init__(self, graphics_engine: GraphicsEngine, time_engine: TimeEngine, start_time: float, finish_time: float, draw_function: callable, object_with_references: Iterable, *args):
        """ :param args: draw function's arguments """
        self._graphics_engine = graphics_engine
        self._time_engine = time_engine
        self._start_time = start_time
        self._finish_time = finish_time
        self._draw = draw_function
        self.args = args
        self._object_with_references = object_with_references

    def draw(self):
        elapsed = self._time_engine.game_time - self._start_time
        total = self._finish_time - self._start_time
        self._draw(*self.args, fps=self._time_engine.fps, elapsed=elapsed, total=total)

    @property
    def start_time(self):
        return self._start_time

    @property
    def finish_time(self):
        return self._finish_time

    def kill(self):
        self._graphics_engine.remove_fx(fx=self)
        for elem in self._object_with_references:
            try:
                elem.remove_fx(self)
            except AttributeError:
                pass


class GraphicsEngine:
    """ Manages graphical effects and background/video """

    import arcade.color as COLOR

    __slots__ = '_beatmap', '_time_engine', '_score_engine', '_keyboard', '_game', '_fxs', '_current_time', '_bg'

    def __init__(self, beatmap: Beatmap, keyboard: Keyboard):
        self._beatmap = beatmap
        self._keyboard = keyboard

        self._fxs = {}  # type: Dict[object, FX]

        self._current_time = 0

        path = self._beatmap.get_folder_path() / self._beatmap.background_filename
        self._bg = arcade.load_texture(file_name=path.as_posix())

    def init_engine(self, game: Game):
        """ Maneuvering circular dependency """
        self._game = game  # for update_rate and window only
        self._time_engine, self._score_engine = game._time_engine, game._score_engine

    def update(self):
        """ Update graphics to match current data """
        self._current_time = self._time_engine.game_time

    def force_update(self):
        self._keyboard.change_resolved = False
        for key in self._keyboard.keys.values():
            key.change_resolved = False

    def on_draw(self):
        """ Draws everything on the screen """
        arcade.start_render()

        self._draw_background()

        self._draw_keyboard()

        self._draw_fx()

        self._draw_clock()
        self._draw_combo()
        self._draw_score()
        self._draw_total_accuracy()
        self._draw_overall_grade()
        self._draw_accuracy_bar()

        self._draw_game_time()
        self._draw_fps()

        self._draw_pointer()

    def _draw_background(self):
        scale = min(self._game.window.width / self._bg.width, self._game.window.height / self._bg.height)
        self._bg.draw(self._game.window.width//2, self._game.window.height//2, self._bg.width*scale, self._bg.height*scale)

    def _draw_keyboard(self):
        """ Draw keyboard """
        keyboard = self._keyboard

        if not keyboard.change_resolved:
            keyboard.shape = arcade.create_rectangle(
                keyboard.center_x, keyboard.center_y, keyboard.width, keyboard.height, keyboard.rgba,
                border_width=keyboard.border_width, tilt_angle=keyboard.tilt_angle, filled=keyboard.filled)
            keyboard.change_resolved = True

        for key in self._keyboard.keys.values():
            if not key.change_resolved:
                key.shape = arcade.create_rectangle(
                    key.center_x, key.center_y, key.width, key.height, key.rgba,
                    border_width=key.border_width, tilt_angle=key.tilt_angle, filled=key.filled)
                key.change_resolved = True

        for shape in [keyboard.shape] + [key.shape for key in keyboard.keys.values()]:
            shape.draw()

    def _register_fx(self, fx: FX, hash = None):
        """ Add `fx` to to-draw stack """
        if hash is None:
            number = self._time_engine.game_time + random()
            self._fxs[number.__hash__()] = fx
        else:
            self._fxs[hash] = fx

    def remove_fx(self, *, fx: FX = None, hash=None):
        if hash is not None:
            self._fxs.pop(hash)
        else:
            to_remove = []
            for k, v in self._fxs.items():
                if v == fx:
                    to_remove.append(k)
            for elem in to_remove:
                self._fxs.pop(elem)
            raise AssertionError

    def _draw_fx(self):
        """ Draw fx that are on-going """
        for fx in self._fxs.values():
            fx.draw()

    def add_grade_fx(self, key: Key, grade):
        """ Draw fx showing grade of the beat pressed at `key`' """
        pass

    def add_key_press_fx(self, key: Key):
        """ Draw fx showing key pressing at `key` """
        pass

    def add_key_release_fx(self, key: Key):
        """ Draw fx showing key releasing at `key` """
        pass

    def add_hit_object_animation(self, key: Key, hit_object: HitObject):
        """ Draw incoming hit_object """
        def f(*args, **kwargs):
            center_x, center_y, width, height, rgba, tilt_angle = args

            elapsed = kwargs.pop('elapsed', None)
            total = kwargs.pop('total', None)

            arcade.draw_rectangle_filled(center_x, center_y,
                                         width * elapsed / total,
                                         height * elapsed / total,
                                         rgba,
                                         tilt_angle=tilt_angle)

        rgba_ = GraphicsEngine.COLOR.PINK

        fx = FX(self, self._time_engine, self._current_time, hit_object.reach_times[0], f, [key],
                key.center_x, key.center_y, key.width, key.height, rgba_, key.tilt_angle)
        self._register_fx(fx, hit_object)

    def _draw_pointer(self):
        """ Draw custom pointer """
        pass

    def _draw_clock(self):
        """ Draw clock showing game progress """
        pass

    def _draw_combo(self):
        """ Draw current combo"""
        combo = self._score_engine.combo
        output = f"combo: {combo}"
        arcade.draw_text(output, 20, self._game.window.height // 2 - 60, arcade.color.WHITE, 16)

    def _draw_score(self):
        """ Draw total score"""
        score = self._score_engine.score
        output = f"score: {score}"
        arcade.draw_text(output, 20, self._game.window.height // 2 + 30, arcade.color.WHITE, 16)

    def _draw_total_accuracy(self):
        """ Draw total accuracy """
        pass

    def _draw_overall_grade(self):
        """ Draw overall grade """
        pass

    def _draw_accuracy_bar(self):
        """ Draw accuracy bar """
        pass

    def _draw_fps(self):
        """ Show FPS on screen """
        fps = self._time_engine.fps
        output = f"FPS: {fps:.1f}"
        arcade.draw_text(output, 20, self._game.window.height // 2, arcade.color.WHITE, 16)

    def _draw_game_time(self):
        """  """
        time = self._time_engine.game_time
        output = f"time: {time:.3f}"
        arcade.draw_text(output, 20, self._game.window.height // 2 - 30, arcade.color.WHITE, 16)


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

    def generate_video(self) -> pyglet.media.Source:
        """ Generate and return a video that can be played, played, paused, replayed
        , and set time. """
        pass

    def generate_hit_objects(self, score_engine: ScoreEngine) -> List[HitObject]:
        """ Generate and return a list of processed hit_objects """
        from random import choice, seed
        import key
        seed(round(sum(self._hit_times), 3))
        hit_objects = [
            HitObject(self, score_engine, hit_time, choice(key.normal_keys), HitObject.TYPE.TAP)
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
        '_animation_times',
        '_symbol',
        '_type',
        '_press_times',
        '_grades',
        '_beatmap',
        '_engine',
        '_state'
    )

    def __init__(self,
                 beatmap: Beatmap,
                 score_engine: ScoreEngine,
                 time: Union[Iterable[float], float],
                 symbol: Union[Iterable[int], int],
                 note_type: Type):
        """  """
        self._reach_times, self._symbol = self._filter_input(time, symbol, note_type)
        self._press_times = []
        self._type = note_type
        self._calculate_animation_times(beatmap.BPM, beatmap.AR)
        self._beatmap = beatmap
        self._engine = score_engine
        self._state = HitObject.STATE.INACTIVE
        self._grades = []

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
    def hit_sound(self) -> int:
        """ Return hit_sounds of object """
        # TODO only return normal for now
        return 0

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


class KeyboardModel:
    """ Data collection for different keyboard types """
    def __int__(self):
        pass


class HitObjectManager:
    """ Manages sending hit_objects to keys and GraphicEngine"""
    def __init__(self, hit_objects: List[HitObject], keyboard: Keyboard):
        self._keys = keyboard.keys
        self._incoming = self._hit_objects = hit_objects
        self._sent = []  # type: List[HitObject]
        self._passed = []  # type: List[HitObject]

    def init_engine(self, game: Game):
        """  """
        self._time_engine = game._time_engine
        self._graphics_engine = game._graphics_engine
        self._audio_engine = game._audio_engine
        self._score_engine = game._score_engine

    def update(self):
        time = self._time_engine.game_time
        send = []
        for hit_object in self._incoming:
            if time >= hit_object.animation_times[0]:
                key = self._keys[hit_object.symbol]
                key.hit_object = hit_object
                self._graphics_engine.add_hit_object_animation(key, hit_object)
                hit_object.change_state('active')
                send.append(hit_object)
        for hit_object in self._sent:
            if time > hit_object.reach_times[-1]:
                if hit_object.state != HitObject.STATE.PASSED:
                    self._change_stack_and_remove_fx(hit_object)
                    self._score_engine.register_hit(hit_object, -1, hit_object.type)
                    key = self._keys[hit_object.symbol]
                    key.remove_hit_object()
                    hit_object.change_state('passed')
        if send:
            for elem in send:
                self._incoming.remove(elem)
            self._sent.extend(send)

    def on_key_press(self, symbol: int, modifiers: int):
        try:
            key = self._keys[symbol]
        except KeyError:
            key = None
        hit_object = None  # type: Optional[HitObject]
        if key:
            key.press()
            self._audio_engine.play_sound(0, 'soft')
            try:
                hit_object = key.hit_object
            except AttributeError:
                print('no object')
        if hit_object:
            try:
                time = self._time_engine.game_time
                hit_object.press(time)
                self._score_engine.register_hit(hit_object, time, hit_object.type)
                if hit_object.state == HitObject.STATE.PASSED:
                    key.remove_hit_object()
                    self._graphics_engine.remove_fx(hash=hit_object)
            except TimeoutError:
                self._change_stack_and_remove_fx(hit_object)
                key.remove_hit_object()
                self._graphics_engine.remove_fx(hash=hit_object)

    def on_key_release(self, symbol: int, modifiers: int):
        try:
            key = self._keys[symbol]
        except KeyError:
            key = None
        if key:
            try:
                key.hit_object.press(self._time_engine.game_time)
            except TimeoutError:
                self._change_stack_and_remove_fx(key.hit_object)
                key.remove_hit_object()
            except AttributeError:
                pass

    def _change_stack_and_remove_fx(self, hit_object: HitObject):
        for elem in self._sent.copy():
            if elem == hit_object:
                self._sent.remove(hit_object)
                self._passed.append(hit_object)
                self._graphics_engine.remove_fx(hash=hit_object)


class Game:
    """ """
    from constants import GameState as State, GAME_STATE as STATE

    def __init__(self, width, height, song: str, difficulty: str):
        filepath = self.get_beatmap_filepath(song, difficulty)
        if filepath is None:
            raise AssertionError
        self._beatmap = Beatmap(filepath)
        self._score_engine = ScoreEngine(beatmap=self._beatmap)
        self._time_engine = TimeEngine()
        self._audio_engine = AudioEngine(beatmap=self._beatmap)
        keyboard_.set_scaling(5)
        self._keyboard = Keyboard(width//2, height//2, model='small notebook', color=arcade.color.LIGHT_BLUE, alpha=150)
        self._graphics_engine = GraphicsEngine(beatmap=self._beatmap, keyboard=self._keyboard)
        self._keyboard.set_graphics_engine(self._graphics_engine)

        self._hit_objects = self._beatmap.generate_hit_objects(score_engine=self._score_engine)
        self._manager = HitObjectManager(hit_objects=self._hit_objects, keyboard=self._keyboard)
        self._state = Game.STATE.GAME_PAUSED
        self._update_rate = 1/60

        for engine in (self._audio_engine, self._score_engine, self._time_engine, self._graphics_engine, self._manager):
            engine.init_engine(self)

    def set_window(self, window: arcade.Window):
        self.window = window

    def start(self):
        """ Start the game """
        self._state = Game.STATE.GAME_PLAYING
        self._audio_engine.song.play()
        self._time_engine.start()

    def pause(self):
        """ Pause the game """
        pass

    def update(self, delta_time: float):
        self._manager.update()
        self._graphics_engine.update()

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        """ This is called during the idle time when it should be called """
        self._time_engine.tick()
        self._graphics_engine.on_draw()

        time = self._audio_engine.song.time
        output = f"audio time: {time:.3f}"
        arcade.draw_text(output, 20, self.window.height // 2 - 90, arcade.color.WHITE, 16)

    def on_resize(self, width: float, height: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key_.P:
            if self.state != Game.STATE.GAME_PLAYING:
                self.start()
        if symbol == 99 and modifiers & 1 and modifiers & 2:
            # CTRL + SHIFT + C to close, for fullscreen emergency
            # TODO: Find a good way to exit
            pyglet.app.exit()

        self._manager.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        try:
            key = self._keyboard.keys[symbol]
        except KeyError:
            key = None
        if key:
            key.release()
            hit_object = key.hit_object
            if hit_object:
                if hit_object.type == HitObject.TYPE.HOLD:
                    hit_object.press(self._time_engine.game_time)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      buttons: int, modifiers: int):
        pass

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        pass

    @property
    def update_rate(self):
        """ Return the update rate (ideal FPS) """
        return self._update_rate

    @update_rate.setter
    def update_rate(self, new_rate: float):
        """ Set the update rate (ideal FPS) """
        assert isinstance(new_rate, float)
        self._update_rate = new_rate

    @property
    def state(self):
        """ Return current state of the instance """
        return self._state

    @staticmethod
    def get_beatmap_filepath(song: str, difficulty: str) -> Optional[Path]:
        """ Return the filepath to .osu file given the name and
        difficulty of the song. """
        songs = Path('resources/Songs').rglob(f'*{song}*')
        try:
            for song in songs:
                if difficulty == '*' and song.suffix == '.osu':
                    return song
                if difficulty in song.name and song.suffix == '.osu':
                    return song
        except StopIteration:
            return
        return


def swap_codecs():
    """ Because pyglet is still buggy we need this to ensure ffmpeg is used """
    decoders = pyglet.media.codecs._decoders
    assert "pyglet.media.codecs.ffmpeg.FFmpegDecoder" in str(decoders)  # assure that it exists
    while str(decoders[0])[:41] != "<pyglet.media.codecs.ffmpeg.FFmpegDecoder":
        # cycle until decoder is ffmpeg
        temp = decoders.pop(0)
        decoders.append(temp)


class GameWindow(arcade.Window):
    def __init__(self):
        """ Create game window """

        super().__init__(1920, 1080, "musicality",
                         fullscreen=False, resizable=True, update_rate=1/60)

        arcade.set_background_color(arcade.color.BLACK)
        swap_codecs()
        self.game = Game(1920, 1080, 'MONSTER', 'NORMAL')
        self.game.set_window(self)

    def update(self, delta_time: float):
        self.game.update(delta_time)

    def on_update(self, delta_time: float):
        self.game.on_update(delta_time)

    def on_draw(self):
        self.game.on_draw()

    def on_resize(self, width: float, height: float):
        self.game.on_resize(width, height)

    def on_key_press(self, symbol: int, modifiers: int):
        self.game.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.game.on_key_release(symbol, modifiers)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.game.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      buttons: int, modifiers: int):
        self.game.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.game.on_mouse_release(x, y, button, modifiers)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.game.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def state(self):
        """ Return current state of the instance """
        return self.game.state


def main():
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
