import time
from abc import ABCMeta, abstractmethod


class EasingBase(metaclass=ABCMeta):
    """ Base for easing functions """
    def __init__(self, duration: float, start: float = 0, end: float = 1, reverse: bool = False):
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

    @abstractmethod
    def func(self, t: float, *args, **kwargs):
        """ Override this. Function should be dependent on `t` """
        pass

    def start(self):
        """ Start easing """
        self.start_time = self.time()

    def __call__(self, *args, **kwargs):
        """ Call the function using eased time """
        elapsed = self.time() - self.start_time
        t = elapsed/self.duration
        if t > self.end:
            self.start_time = None
            raise TimeoutError('passed easing time')
        elif t < self.start:
            raise AssertionError
        t = self.ease(t)
        self.func(t, *args, **kwargs)

    @abstractmethod
    def ease(self, t: float) -> float:
        """ The actual easing function """
        pass




