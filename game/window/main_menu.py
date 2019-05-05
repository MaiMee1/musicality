from game.window.window import BaseWindow, MainWindow

from pyglet.window import key


class MainMenu(BaseWindow):
    """ The first state the user sees """
    def __init__(self, window: MainWindow):
        super().__init__(window)
        self.caption = 'musicality - Main Menu'

    def on_draw(self):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)
        if symbol == key.ENTER:
            self.change_state('song select')

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        pass

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        pass

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        pass

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        pass

    def change_state(self, state: str):
        if state == 'song select':
            from .song_select import SongSelect
            self._window.change_handler(SongSelect(self._window))

