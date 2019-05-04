from __future__ import annotations
from typing import Union


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


class TimeEngine:
    """ Manages time. Unit is in seconds. """

    __slots__ = 'time', '_frame_times', '_t', '_start_time', '_dt', '_start', '_absolute_time', '_audio'

    def __init__(self, maxlen: int = 60):
        import time
        import collections
        self.time = time.perf_counter
        self._frame_times = collections.deque(maxlen=maxlen)
        self._t = self._start_time = self._absolute_time = self.time()
        self._dt = 0
        # Ensure that deque is not empty and sum() != 0
        self.tick()
        self._start = False

        self._audio = None

    def tick(self):
        """ Call to signify one frame passing """
        t = self.time()
        self._dt = t - self._t
        self._t = t
        self._frame_times.append(self._dt)

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
            return 0.

    @property
    def play_time(self) -> float:
        """ Return current time at function call """
        return self.time() - self._absolute_time

    @property
    def dt(self) -> float:
        """ Return time difference of this and last frame """
        return self._dt

    # requires audio (should be quickly depreciated)

    def set_audio(self, audio: 'Audio'):
        """ Set audio to reference game_time to """
        self._audio = audio

    @property
    def game_time(self) -> float:
        """ Return time for the game. Same as audio time. """
        if self._audio:
            return self._audio.time
        if self._start:
            return self.play_time
        return 0.
