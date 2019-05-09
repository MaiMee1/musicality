import time
from abc import ABCMeta, abstractmethod


class EasingBase(metaclass=ABCMeta):
    """ Base for easing functions """

    __slots__ = 'start', 'end', 'duration', 'time', 'start_time', 'reverse'

    def __init__(self, duration: float, start: float = 0, end: float = 1, reverse: bool = False, finalise = True):
        """Base for easing functions.

        Everything should be normalised to [0, 1].

        :param duration: total time duration (seconds)
        :param start: starting position of function
        :param end: ending position of function
        :param reverse: True if go from end to start
        """
        self.reverse = reverse
        if start > end:
            start, end = end, start
            self.reverse = True
        self.start = start
        self.end = end
        self.duration = duration
        self.time = time.perf_counter
        self.start_time = None
        self.finalise = finalise

    @abstractmethod
    def func(self, t: float, **kwargs):
        """ Override this. Function should have domain [0, 1] """
        pass

    def begin(self):
        """ Start easing """
        self.start_time = self.time()

    def __call__(self, **kwargs):
        """ Call the function using eased time """
        try:
            assert self.start_time is not None, 'begin easing first'
        except AssertionError:
            self.begin()
        elapsed = self.time() - self.start_time
        t = elapsed/self.duration
        if t > self.end:
            self._finalise(**kwargs)
        elif t < self.start:
            raise AssertionError
        t = self.ease(t)
        return self.func(t, **kwargs)

    def _finalise(self, cache=[], **kwargs):
        """ Tries to ensure final value is reached """
        if not cache and self.finalise:
            cache.append(1)
            return self.func(1, **kwargs)
        self.start_time = None
        raise TimeoutError('passed easing time')

    @abstractmethod
    def ease(self, t: float) -> float:
        """ Override this. The actual easing function """
        pass




