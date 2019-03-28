import collections
import time

import arcade
import pyglet

import keyboard

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Game Window"


class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        """ Call this every frame """
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return len(self.frame_times) / sum(self.frame_times)


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=False, resizable=True)

        arcade.set_background_color(arcade.color.BLACK)

        keyboard.set_scaling(5)
        self.keyboard = keyboard.Keyboard(width // 2, height // 3,
                                          model='small notebook',
                                          color=arcade.color.LIGHT_BLUE,
                                          alpha=150)
        self.update_rate = 1/60
        self._set_update_rate(1/60)
        self.fps = FPSCounter()
        self.keyboard.redraw(deep=True)

    def on_update(self, delta_time: float):
        self.fps.tick()
        self.keyboard.update()

    def on_draw(self):
        arcade.start_render()
        self.keyboard.draw()

        fps = self.fps.get_fps()
        output = f"FPS: {fps:.1f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT//2, arcade.color.WHITE, 16)

    def on_resize(self, width: float, height: float):
        self.keyboard = keyboard.Keyboard(width // 2, height // 3,
                                          model='small notebook',
                                          color=arcade.color.LIGHT_BLUE,
                                          alpha=150)
        self.keyboard.redraw()

    def on_key_press(self, symbol: int, modifiers: int):
        # print(symbol, modifiers)
        if symbol == 99 and modifiers & 1 and modifiers & 2:  # CTRL + SHIFT + C to close
                                                              # for fullscreen emergency
            # TODO: Find a good way to exit
            pyglet.app.exit()
        self.keyboard.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.keyboard.on_key_release(symbol, modifiers)

    def _set_update_rate(self, rate: float):
        self.set_update_rate(rate)
        self.update_rate = rate


def main():
    GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
