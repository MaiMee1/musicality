from typing import List

import arcade

from game.window.window import BaseForm, Main
from game.window import key
from game.graphics.element import Button, UIElement, Text


class MainMenu(BaseForm):
    """ The first state the user sees """
    def __init__(self, window: Main):
        super().__init__(window)
        self.caption = 'musicality - Main Menu'

        self.elements = []  # type: List[UIElement]

        exit_text = Text('Exit', 0, 0, arcade.color.WHITE, 20)
        exit_button = Button(0, 0, 100, 60, arcade.color.RED_VIOLET)
        exit_button.left = 50
        exit_button.bottom = 50
        exit_text.position = exit_button.position
        exit_text.move(-20, -10)
        exit_button.text = exit_text
        exit_button.action['on_press'] = self.on_close

        exit_button.drawable[0].recreate_vbo()

        self.elements.append(exit_button)

    def on_draw(self):
        self.clear()
        # DRAW UI
        for element in self.elements:
            element.draw()

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)
        if symbol == key.ENTER:
            self.change_state('song select')

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        # UI MANAGEMENT
        for element in self.elements:
            if element.is_inside(x, y):
                element.on_hover()

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        # UI MANAGEMENT
        for element in self.elements:
            if element.is_inside(x, y):
                element.on_press()

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        # UI MANAGEMENT
        for element in self.elements:
            if element.pressed:
                element.on_release()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        pass

    def change_state(self, state: str):
        if state == 'song select':
            from .song_select import SongSelect
            self._window.change_handler(SongSelect(self._window))

