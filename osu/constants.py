# Constants/Options for osu module

from collections import namedtuple

_sample_set = namedtuple('sample_set', ['NORMAL', 'SOFT', 'DRUM'])
_sound = namedtuple('sound', ['AUTO', 'NORMAL', 'SOFT', 'DRUM'])
_type = namedtuple('HitObject_type', ['CIRCLE', 'SLIDER', 'SPINNER'])
_version = namedtuple('version', ['EASY', 'NORMAL', 'HARD', 'INSANE'])

# -sample_set
SAMPLE_SET = _sample_set('Normal', 'Soft', "Drum")

# -sound
SOUND = _sound('Auto', 'Normal', 'Soft', 'Drum')

# -version
VERSION = _version('Easy', 'Normal', 'Hard', 'Insane')

# TimingPoint
ON = 1
OFF = 0

# HitObject
CIRCLE = (1, 5, 21, 37)  # (no new combo, new +1, new +2, new +3)
SLIDER = (2, 6, 22, 38)
SPINNER = (8, 12, 28, 44)
