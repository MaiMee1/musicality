class Temp(object):
    """ Temporary class for one time internal use """
    def __init__(self, **kwargs):
        """ Make each keyword argument into an attribute """
        for k, v in kwargs.items():
            self.__setattr__(k, v)
