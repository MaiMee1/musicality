from collections import namedtuple
from type_ import *

# for Beatmap
SAMPLE = ('hitnormal', 'hitwhistle', 'hitfinish', 'hitclap')
SAMPLE_SET = ('normal', 'soft', 'drum')

SAMPLE_NAMES = set('-'.join((x, y)) for x in SAMPLE_SET for y in SAMPLE)
# SAMPLE_SET_FILENAMES = map(lambda x: '-'.join(x), itertools.product(_sample_set, _sample))

_temp = namedtuple('HitObjectConstant', ['TAP', 'HOLD'])
HIT_OBJECT_TYPE = _temp(HitObjectType(1), HitObjectType(2))

_temp = namedtuple('HitObjectConstant', ['INACTIVE', 'ACTIVE', 'PASSED'])
HIT_OBJECT_STATE = _temp(*map(HitObjectState, range(3)))

_temp = namedtuple('GameConstant', ['MAIN_MENU', 'OPTIONS', 'SONG_SELECT', 'GAME_PAUSED', 'GAME_PLAYING', 'GAME_FINISH'])
GAME_STATE = _temp(*map(GameState, range(6)))

_temp = namedtuple('MouseConstant', ['IDLE', 'HOVER', 'PRESS', 'TEXT'])
MOUSE_STATE = _temp(*map(MouseState, range(4)))

_temp = namedtuple('UIElementConstant', ['INACTIVE', 'ACTIVE'])
UI_ELEMENT_STATE = _temp(*map(UIElementState, range(2)))

_temp = namedtuple('HitSoundConstant', ['CLAP', 'FINISH', 'WHISTLE', 'NORMAL'])
HIT_SOUND = _temp(8, 4, 2, 0)

HIT_SOUND_MAP = {
    0: ('hitnormal',), 2: ('hitnormal', 'hitwhistle',), 4: ('hitnormal', 'hitfinish',), 8: ('hitnormal', 'hitclap',),
    6: ('hitnormal', 'hitwhistle', 'hitfinish'), 10: ('hitnormal', 'hitwhistle', 'hitclap'),
    12: ('hitnormal', 'hitfinish', 'hitclap'), 14: ('hitnormal', 'hitwhistle', 'hitfinish', 'hitclap')
}
