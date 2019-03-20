import arcade

from keyboard import Keyboard, set_scaling

# SCREEN_WIDTH = 1920
# SCREEN_HEIGHT = 1080
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Game Window"


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=False, resizable=True)

        arcade.set_background_color(arcade.color.BLACK)

        set_scaling(5)
        self.keyboard = Keyboard(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3,
                                 model='small notebook',
                                 color=arcade.color.LIGHT_BLUE,
                                 alpha=150)

    def on_draw(self):
        arcade.start_render()
        self.keyboard.update()
        self.keyboard.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        print(symbol, modifiers)
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        self.keyboard.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.keyboard.on_key_release(symbol, modifiers)


def main():
    GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
