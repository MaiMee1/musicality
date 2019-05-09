import arcade

from game.graphics.primitives import Drawable, Movable


class Sprite(arcade.Sprite, Drawable, Movable):

    point_sprite = arcade.Sprite()
    point_sprite.points = (0, 0)

    def is_inside(self, x: float, y: float):
        Sprite.point_sprite.points = (x, y)
        return arcade.check_for_collision(self, Sprite.point_sprite)

    def move(self, delta_x: float, delta_y: float):
        self.position = self.position[0]+delta_x, self.position[1]+delta_y
