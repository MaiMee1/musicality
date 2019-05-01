from collections import namedtuple
from typing import NewType
import itertools

# for Beatmap
SAMPLE = ('hitnormal', 'hitwhistle', 'hitfinish', 'hitclap')
SAMPLE_SET = ('normal', 'soft', 'drum')

SAMPLE_NAMES = set('-'.join((x, y)) for x in SAMPLE_SET for y in SAMPLE)
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

HIT_SOUND_MAP = {
    0: ('hitnormal',), 2: ('hitnormal', 'hitwhistle',), 4: ('hitnormal', 'hitfinish',), 8: ('hitnormal', 'hitclap',),
    6: ('hitnormal', 'hitwhistle', 'hitfinish'), 10: ('hitnormal', 'hitwhistle', 'hitclap'),
    12: ('hitnormal', 'hitfinish', 'hitclap'), 14: ('hitnormal', 'hitwhistle', 'hitfinish', 'hitclap')
}


"""Finished Master's degree 5 years ago; finished doctorate if useful; have job experience somewhere good; get life going; found someone; have enough money to use and send to parents; made something useful that made headlines; """