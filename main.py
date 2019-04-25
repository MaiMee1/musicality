from __future__ import annotations

from pathlib import Path
from io import StringIO
from typing import Any, Union, Optional, Tuple, List, Dict, NewType, TextIO, Iterable, Callable
import warnings

import arcade
import pyglet

import key as key_
import new_keyboard as keyboard_
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

    __slots__ = '_source', '_engine', '_player'

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
            # FIXME DO NOT USE resource
            if filepath:
                if not absolute:
                    filepath = Path().resolve() / filepath
                pyglet.resource.path.append(str(filepath.parent))
                pyglet.resource.reindex()
                self._source = pyglet.media.load(filepath.name)
            else:
                raise TypeError("Audio() missing 1 required keyword argument: 'filepath'")
        self._engine: AudioEngine
        self._player: pyglet.media.Player

    @property
    def source(self):
        """ Return the source of this audio """
        return self._source

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

    @property
    def player(self) -> Optional[pyglet.media.Player]:
        """ Return the player of this audio """
        try:
            return self._player
        except AttributeError:
            return

    def set_player(self, new_player: pyglet.media.Player):
        """ Set player to `new_player` """
        self._player = new_player


class AudioEngine:
    """ Manages audio """

    __slots__ = 'beatmap', '_sample_sets', '_song', '_audios', '_players'

    from constants import SAMPLE_NAMES
    from constants import HIT_SOUND_MAP

    def __init__(self, beatmap: Beatmap, time_engine: TimeEngine):
        self.beatmap = beatmap
        self._sample_sets = []  # type: List[Dict[str, Audio]]

        self._song = Audio(filename=beatmap.audio_filename, loader=beatmap.resource_loader)

        self._audios = []  # type: List[Audio]
        self._players = []  # type: List[pyglet.media.Player]

        self.register(self._song)

    # def load_song(self, song_path: Optional[Path]):
    #     """ Get things going. (Re)Load file from path and initialize
    #     for playing. Set game_time to zero - wait_time. """
    #     pass

    def _generate_sample_set(self):
        d = {name: Audio() for name in self.beatmap.get_samples_filenames()}
        for name in self.SAMPLE_NAMES:
            if name not in d.keys():
                d[name] = AudioEngine._load_default(name)
        self._sample_sets.extend(d)
        pass

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

    def play_sound(self, hit_sound: int):
        """ Play hit_sound according to code given """
        assert hit_sound in AudioEngine.HIT_SOUND_MAP.keys()
        try:
            samples = AudioEngine.HIT_SOUND_MAP[hit_sound]
            for sample in samples:
                sample = 'normal-' + sample + '.wav'
                try:
                    self._sample_sets[0][sample].play()
                except:
                    pass
        except:
            pass

    @property
    def song(self) -> Audio:
        """ Return the song """
        return self._song

    def _get_player(self, audio) -> (Optional[pyglet.media.Player]):
        """ Get a player has audio as the current source or recycle one that is not playing or create a new one.
        Returns: Player, source_loaded (bool) """
        match = [player for player in self._players if player.source == audio]
        if match:
            return match
        return None

    def _add_player(self, player=None) -> pyglet.media.Player:
        """ Add `player` to list or generate a new one and add to list """
        if player is None:
            player = pyglet.media.Player()
        self._players.append(player)
        return player

    def play(self, audio: Audio):
        """ Play the audio if stopped """
        player = self._add_player()
        player.queue(audio.source)
        player.play()

    def stop(self, audio: Audio):
        """ Stop the audio if playing """
        players = self._get_player(audio)
        if players is not None:
            player = players[0]
            player.pause()
            player.seek(0)

    def playing(self, audio: Audio) -> bool:
        """ Return True if audio is playing, False otherwise """
        players = self._get_player(audio)
        if players is not None:
            player = players[0]
            return player.playing
        return False

    def pause(self, audio: Audio):
        """ Pause the audio if playing """
        players = self._get_player(audio)
        if players is not None:
            player = players[0]
            player.pause()

    def restart(self, audio: Audio):
        """ Play the audio again from the beginning """
        players = self._get_player(audio)
        if players is not None:
            player = players[0]
            player.seek(0)

    def seek(self, audio: Audio, time: Union[str, int ,float]):
        """ Seek audio to `time` """
        players = self._get_player(audio)
        if players is not None:
            player = players[0]
            player.seek(float(time))

    def time(self, audio: Audio) -> Tuple[float]:
        """ Return current time of audio """
        players = self._get_player(audio)
        if players is not None:
            return tuple(player.time for player in players)


class ScoreEngine:
    """ Manages calculation of score, combo, grade, etc. """
    def __init__(self, beatmap: Beatmap):
        from collections import deque
        self.beatmap = beatmap
        self._score = 0
        self._combo = 0
        self._perfect = True
        self._not_missed = True
        self._accuracy_stack = deque(maxlen=20)
        self._grade_stack = []

    def register_hit(self, hit_object: HitObject, time: float, type: HitObject.Type):
        # TODO
        accuracy = self._calculate_accuracy(time)
        grade = self._calculate_grade(accuracy)
        score = self._calculate_score(grade, type)

        self._accuracy_stack.append(accuracy)
        self._grade_stack.append(abs(1-accuracy))
        if self._perfect:
            if grade != 'perfect':
                self._perfect = False
        if grade != 'miss':
            self._combo += 1
        else:
            if self._not_missed:
                self._not_missed = False
        hit_object.add_grade(grade)
        self._score += score

    def _calculate_accuracy(self, time: float) -> float:
        OD = self.beatmap.OD
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
        return self._combo

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


class GraphicsEngine:
    """ Manages graphical effects and background/video """

    __slots__ = '_beatmap', '_time_engine', '_score_engine', '_keyboard', '_game'

    def __init__(self, game: Game, beatmap: Beatmap, time_engine: TimeEngine, score_engine: ScoreEngine, keyboard: Keyboard):
        self._game = game  # for update_rate and window only
        self._beatmap = beatmap
        self._time_engine = time_engine
        self._score_engine = score_engine
        self._keyboard = keyboard

    def update(self):
        """ Update graphics to match current data """
        pass

    def on_draw(self):
        """ Draws everything on the screen """
        arcade.start_render()
        self._draw_keyboard()

        self._draw_current_fx()

        self._draw_clock()
        self._draw_combo()
        self._draw_score()
        self._draw_total_accuracy()
        self._draw_overall_grade()
        self._draw_accuracy_bar()

        self._draw_fps()

        self._draw_pointer()

    def _draw_keyboard(self):
        """ Draw keyboard """
        self._keyboard.draw()

    def _draw_current_fx(self):
        """ Draw fx that are on-going """
        pass

    def _draw_pointer(self):
        """ Draw custom pointer """
        pass

    def _draw_clock(self):
        """ Draw clock showing game progress """
        pass

    def _draw_combo(self):
        """ Draw current combo"""
        pass

    def _draw_score(self):
        """ Draw total score"""
        pass

    def _draw_total_accuracy(self):
        """ Draw total accuracy """
        pass

    def _draw_overall_grade(self):
        """ Draw overall grade """
        pass

    def _draw_accuracy_bar(self):
        """ Draw accuracy bar """
        pass

    def _draw_grade_fx(self, key: Key, grade):
        """ Draw fx showing grade of the beat pressed at `key`' """
        pass

    def _draw_key_press_fx(self, key: Key):
        """ Draw fx showing key pressing at `key` """
        pass

    def _draw_key_release_fx(self, key: Key):
        """ Draw fx showing key releasing at `key` """
        pass

    def _draw_fps(self):
        """ Show FPS on screen """
        fps = self._time_engine.fps
        output = f"FPS: {fps:.1f}"
        arcade.draw_text(output, 20, self._game.window.height // 2, arcade.color.WHITE, 16)


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

    def get_samples_filenames(self) -> List[str]:
        """ Return name of the custom sample that exists """
        filenames = []
        for name, path in self._sample.items():
            try:
                path.relative_to(Path().resolve())
                filenames.append(name)
            except ValueError:
                pass
        return filenames

    def generate_video(self) -> pyglet.media.Source:
        """ Generate and return a video that can be played, played, paused, replayed
        , and set time. """
        pass

    def generate_hit_objects(self, score_engine: ScoreEngine) -> List[HitObject]:
        """ Generate and return a list of processed hit_objects """
        from random import choice
        import key
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

    # def get_audio_path(self, absolute=False) -> Path:
    #     """ Return path to the audio file-- the song (mostly .mp3) --of
    #     the instance. """
    #     if absolute:
    #         return Path().resolve() / self._audio_filepath
    #     return  self._audio_filepath
    #

    # def generate_audio(self) -> Audio:
    #     """ Generate and return an audio player object """
    #     pass
    #     # return Audio(filename=self.audio_filename, loader=self._loader)

    # def get_hit_sound_paths(self, absolute=False) -> List[Path]:
    #     """ Return a list of paths to hit_sounds-- sounds a keypress
    #     maps to (mostly .wav) --files of the instance. """
    #     pass
    #

    # def generate_hit_sounds(self) -> List[Audio]:
    #     """ Generate and return a list of audio objects """
    #     return [Audio(filepath=path) for path in self._sample.values()]
    #
    # def get_hit_sound(self, name: str) -> Audio:
    #     """ Generate and return an audio object """
    #     assert name in Beatmap.SAMPLE_NAMES
    #     return Audio(filepath=self._sample[name])
    #
    # def get_background_path(self, absolute=False) -> Optional[Path]:
    #     """ Return path to background image(s?) of the instance """
    #     if self._background_filename is None:
    #         return None
    #     if absolute:
    #         return self.get_folder_path(absolute=True) / self._background_filename
    #     return self.get_folder_path() / self._background_filename
    #
    # @property
    # def background_filename(self) -> Optional[str]:
    #     """ Return name of the background image file """
    #     if self._background_filename is None:
    #         return self._background_filename
    #
    # def background_image(self) -> pyglet.image.AbstractImage:
    #     """ Generate and return an image that can be drawn """
    #     pass
    #
    # def get_video_path(self, absolute=False) -> Optional[Path]:
    #     """ Return path to video of the instance """
    #     if self._video_filename is None:
    #         return None
    #     if absolute:
    #         return self.get_folder_path(absolute=True) / self._video_filename
    #     return self.get_folder_path() / self._video_filename
    #
    # @property
    # def video_filename(self) -> Optional[str]:
    #     """ Return name of the video file """
    #     if self._video_filename is None:
    #         return None
    #     return self._video_filename
    #
    # def video(self) -> pyglet.media.Source:
    #     """ Generate and return a video that can be played, played, paused, replayed
    #     , and set time. """
    #     pass


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
        '_state',
    )

    def __init__(self,
                 beatmap: Beatmap,
                 engine: ScoreEngine,
                 time: Union[Iterable[float], float],
                 symbol: Union[Iterable[int], int],
                 note_type: Type):
        """  """
        self._reach_times, self._symbol = self._filter_input(time, symbol, note_type)
        self._type = note_type
        self._calculate_animation_times(beatmap.BPM, beatmap.AR)
        self._beatmap = beatmap
        self._engine = engine
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

    def _calculate_animation_times(self, BPM: float, AR: float):
        """ Set the _animation_times """
        assert BPM > 0
        assert 0 <= AR <= 10
        AR = AR / 2
        beat = 60 / BPM  # seconds
        delay = beat * (1 + (10 - AR) / 3)  # seconds
        self._animation_times = [reach_time - delay for reach_time in self._reach_times]  # seconds

    def press(self, time: float):
        """ Mark `time` as a press_time if pressable.
        Raise TimeoutError if not pressable """
        if self.state == HitObject.STATE.ACTIVE:
            self._press_times.append(time)
            self._engine.register_hit(self, time, self._type)
        else:
            raise TimeoutError('object is not pressable')
        if len(self._press_times) == HitObject.TYPE_MAXLEN_MAP[self._type]:
            self._state = HitObject.STATE.PASSED

    # @property
    # def reach_times(self) -> List[float]:
    #     """ Return list of times in relation to game_time (seconds)
    #     object needs to be interacted with by the player. """
    #     pass
    #
    # @property
    # def reach_times_ms(self) -> List[int]:
    #     """ Return reach_time in milliseconds """
    #     pass

    @property
    def animation_times(self) -> List[float]:
        """ Return list of times in relation to game_time (seconds)
        graphics engine need to do animations. """
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

    def _dt(self) -> List[float]:
        """ Return the time difference (seconds) between reach_time and
        press_time-- press_time - reach_time --of the instance.
        Negative if pressed early; positive if late. """
        assert self._state == HitObject.STATE.PASSED
        # TODO
        return [press - reach for press, reach in zip(self._press_times, self._reach_times)]


class Key:
    """ Represents a key on the virtual keyboard """
    def __init__(self):
        self._hit_object: HitObject = None

    @property
    def hit_object(self) -> Optional[HitObject]:
        """ """
        if self._hit_object:
            return self._hit_object

    def draw(self):
        """ Draw the element """
        pass

    def press(self):
        pass

    def release(self):
        pass

    @property
    def state(self):
        """ Return the current state of the key """
        pass


class KeyboardModel:
    """ Data collection for different keyboard types """
    def __int__(self):
        pass


class Keyboard:
    """ Represents the board behind keys """
    def __init__(self, center_x: int, center_y: int):
        self.keys: Dict[int, Key]
        keyboard_.set_scaling(5)
        self.keyboard = keyboard_.Keyboard(center_x, center_y,
                                           model='small notebook',
                                           color=arcade.color.LIGHT_BLUE,
                                           alpha=150)
        self.keys = {k: Key() for k in self.keyboard.keys.keys()}

    def draw(self):
        """ Draw the element """
        self.keyboard.draw()

    def location(self) -> (int, int) :
        """ Return the current location in pixels """
        pass

    def set_location(self, center_x: int, center_y: int):
        """ Move the keyboard (and its keys) to new location """
        pass

    def on_key_press(self, symbol: int, modifiers: int, time: float):
        self.keyboard.keys[symbol].on_key_press(symbol, modifiers)
        try:
            key = self.keys[symbol]
        except KeyError:
            key = None
        if key:
            key.press()
            hit_object = key.hit_object
            if hit_object:
                hit_object.press(time)

    def on_key_release(self, symbol: int, modifiers: int, time: float):
        self.keyboard.keys[symbol].on_key_release(symbol, modifiers)
        try:
            key = self.keys[symbol]
        except KeyError:
            key = None
        if key:
            key.release()
            hit_object = key.hit_object
            if hit_object:
                if hit_object.type == HitObject.TYPE.HOLD:
                    hit_object.press(time)


class Game:
    """ """
    from constants import GameState as State, GAME_STATE as STATE

    def __init__(self, width, height, song: str, difficulty: str):
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
        print(1)
        self._beatmap = Beatmap(filepath)
        print(2)
        self._score_engine = ScoreEngine(beatmap=self._beatmap)
        print(3)
        self._time_engine = TimeEngine()
        print(4)
        self._audio_engine = AudioEngine(beatmap=self._beatmap, time_engine=self._time_engine)
        print(5)
        self._keyboard = Keyboard(width//2, height//2)
        print(6)
        self._graphics_engine = GraphicsEngine(self, beatmap=self._beatmap, time_engine=self._time_engine, score_engine=self._score_engine, keyboard=self._keyboard)
        print(7)

        self._hit_objects = self._beatmap.generate_hit_objects(score_engine=self._score_engine)
        print(8)
        self._state = Game.STATE.GAME_PAUSED
        print(9)
        self._update_rate = 1/60

    def set_window(self, window: arcade.Window):
        self.window = window

    def start(self):
        """ Start the game """
        self._state = Game.STATE.GAME_PLAYING
        self._audio_engine.song.play()
        self._time_engine.reset()

    def pause(self):
        """ Pause the game """
        pass

    def update(self, delta_time: float):
        self._graphics_engine.update()

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        """ This is called during the idle time when it should be called """
        self._time_engine.tick()
        self._graphics_engine.on_draw()

    def on_resize(self, width: float, height: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key_.P:
            self.start()
        if symbol == 99 and modifiers & 1 and modifiers & 2:
            # CTRL + SHIFT + C to close, for fullscreen emergency
            # TODO: Find a good way to exit
            pyglet.app.exit()
        self._keyboard.on_key_press(symbol, modifiers, self._time_engine.game_time)

    def on_key_release(self, symbol: int, modifiers: int):
        self._keyboard.on_key_release(symbol, modifiers, self._time_engine.game_time)

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
                if difficulty in song.name:
                    return song
        except StopIteration:
            return
        return


class GameWindow(arcade.Window):
    def __init__(self):
        """ Create game window """

        super().__init__(1920, 1080, "musicality",
                         fullscreen=False, resizable=False, update_rate=1/60)

        arcade.set_background_color(arcade.color.BLACK)
        self.game = Game(1920, 1080, 'Sayonara no Yukue', 'Insane')
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
