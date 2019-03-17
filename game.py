import arcade

from keyboard import create_keyboard_shape

# SCREEN_WIDTH = 1920
# SCREEN_HEIGHT = 1080
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Game Window"


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=False, resizable=True)

        arcade.set_background_color(arcade.color.WHITE)

        self.shape = create_keyboard_shape(SCREEN_WIDTH//2, SCREEN_HEIGHT//3)

    def on_draw(self):
        arcade.start_render()
        self.shape.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        print(symbol, modifiers)
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()


def main():
    GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
