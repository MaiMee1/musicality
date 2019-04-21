from collections import namedtuple
from typing import NewType
import itertools

# for Beatmap
_sample = ('hitnormal', 'hitwhistle', 'hitfinish', 'hitclap')
_sample_set = ('normal', 'soft', 'drum')

SAMPLE_NAMES = ('-'.join((x, y)) for x in _sample_set for y in _sample)
# SAMPLE_SET_FILENAMES = map(lambda x: '-'.join(x), itertools.product(_sample_set, _sample))


class _Temp(object):
    """ Temporary class for one time internal use """
    def __init__(self, **kwargs):
        """ Make each keyword argument into an attribute """
        for k, v in kwargs.items():
            self.__setattr__(k, v)


HitObjectType = NewType('HitObjectType', int)
_temp = namedtuple('HitObjectConstant', ['TAP', 'HOLD'])
HIT_OBJECT_TYPES = _temp(HitObjectType(1), HitObjectType(2))

HitObjectState = NewType('HitObjectState', int)
_temp = namedtuple('HitObjectConstant', ['INACTIVE', 'ACTIVE', 'PASSED'])
HIT_OBJECT_STATES = _temp(HitObjectState(0), HitObjectState(1), HitObjectState(2))

# for Game
GameState = NewType('GameState', int)
_temp = namedtuple('HitObjectConstant', ['MAIN_MENU', 'OPTIONS', 'SONG_SELECT', 'GAME_PAUSED', 'GAME_PLAYING', 'GAME_FINISH'])
GAME_STATE = _temp(*map(GameState, range(6)))

_temp = namedtuple('HitSoundConstant', ['CLAP', 'FINISH', 'WHISTLE', 'NORMAL'])
HIT_SOUND = _temp(8, 4, 2, 0)

