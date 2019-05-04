class Temp:
    """ Temporary class for one time internal use """
    def __init__(self, **kwargs):
        """ Make each keyword argument into an attribute """
        for k, v in kwargs.items():
            self.__setattr__(k, v)


def del_value(d: dict, value, index: int = 1, all: bool = False):
    """ delete `value` from `d` """
    count = 0
    for k, v in ((_, __) for _, __ in d.items()):
        if v == value:
            count += 1
            if all:
                d.pop(k)
            elif count == index:
                d.pop(k)
                break
    if index == -1:
        index = count - 1
        count = 0
        for k, v in ((_, __) for _, __ in d.items()):
            if v == value:
                count += 1
                if count == index:
                    d.pop(k)
                    break
