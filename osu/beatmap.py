from typing import Union, List, Optional, TextIO, Dict, Iterable
from pathlib import Path
from io import StringIO
import warnings

import pyglet

_beatmaps = {}


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
        from game.constants import SAMPLE_NAMES
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
            preview_time = read_until(f, 'PreviewTime: ')
            self._preview_timestamp = int(preview_time) / 1000

            def get_data(container: Dict,
                         str_heads: Iterable[str],
                         keys: Optional[Iterable[str]] = None,
                         to_int: Union[Iterable[str], str, None] = None,
                         to_float: Union[Iterable[str], str, None] = None,
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
                     ('Title:', 'TitleUnicode:', 'Artist:', 'ArtistUnicode:', 'Creator:',
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
                    elif elem.endswith('.JPG'):
                        # WTF? Why would you use an uppercase suffix...
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
        """ Return name of the background file """
        if self._background_filename:
            return self._background_filename

    @property
    def background_filepath(self) -> Optional[Path]:
        """ Return path of the background file """
        if self._background_filename:
            return self.get_folder_path() / self._background_filename

    @property
    def video_filename(self) -> Optional[str]:
        """ Return name of the video file """
        return self._video_filename

    @property
    def sample_filenames(self) -> List[str]:
        """ Return a list of name of custom samples """
        return self._sample_filenames

    @property
    def title(self) -> str:
        return self._metadata['Title']

    @property
    def unicode_title(self) -> str:
        return self._metadata['TitleUnicode']

    @property
    def artist(self) -> str:
        return self._metadata['Artist']

    @property
    def unicode_artist(self) -> str:
        return self._metadata['ArtistUnicode']

    @property
    def creator(self) -> str:
        return self._metadata['Creator']

    @property
    def id(self) -> int:
        if self._metadata['BeatmapID']:
            return self._metadata['BeatmapID']
        return 0

    @property
    def preview_timestamp(self) -> float:
        return self._preview_timestamp

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


def load():
    global _beatmaps

    for folder in Path('resources/Songs/').iterdir():
        temp = {file.stem: Beatmap(file) for file in folder.rglob('*.osu')}
        _beatmaps[folder.name] = temp


def get_beatmaps() -> Dict[str, Dict[str, Beatmap]]:
    if not _beatmaps:
        load()
    return _beatmaps

