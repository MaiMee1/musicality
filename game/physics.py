class Vector2D:
    """ Represents a 2D vector """

    __slots__ = 'x', 'y'

    def __init__(self, *args):
        try:
            x, y = args
        except TypeError:
            try:
                x, y = args[0], args[1]
                assert len(args) == 2, '2D vector'
            except TypeError as e:
                e.args = ('invalid type, use `x` and `y` or iterable with len 2',)
                raise
        self.x: float = x
        self.y: float = y

    def __str__(self):
        return f'Vector2D({self.x}, {self.y})'

    def __add__(self, other):
        try:
            return Vector2D(self.x + other.x, self.y + other.y)
        except AttributeError:
            return Vector2D(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        try:
            return Vector2D(self.x + other.x, self.y + other.y)
        except AttributeError:
            return Vector2D(self.x + other[0], self.y + other[1])

    def __mul__(self, other):
        try:
            return Vector2D(self.x * other.x, self.y * other.y)
        except AttributeError:
            try:
                assert len(other) == 2, '2D vector'
                return Vector2D(self.x * other[0], self.y * other[1])
            except TypeError:
                try:
                    return Vector2D(self.x * other, self.y * other)
                except TypeError as e:
                    e.args = ('valid type include Vector2D, a number, and iterable with len 2',)
                    raise

