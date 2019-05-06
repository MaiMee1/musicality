from typing import List
from functools import partial
from types import MethodType

import arcade

from game.window.window import BaseForm, Main
from game.window import key
from game.graphics.element import Button, UIElement, Text


def create_menu_button(text1: str, text2: str='', color=arcade.color.PURPLE_HEART, secondary_color=arcade.color.RED_VIOLET):
    button = Button(0, 0, 550, 120, color, secondary_color=secondary_color)
    text1_ = Text(text1, button.left+140, button.bottom+48, arcade.color.WHITE, 56)
    text2_ = Text(text2, button.left+180, button.bottom+12, arcade.color.WHITE, 16)
    text2_.visible = False
    button.text = text1_
    button.text2 = text2_
    button.drawable.append(text2_)

    def change_color_to(self, color: (int, int, int)):
        # FIXME goes rainbow when cursor moves out while not finished
        if self.rectangle.color != color:
            dr, dg, db = [(sec - rec) for sec, rec in zip(color, self.rectangle.color)]
            scale = max(dr, dg, db)
            if scale == 0:
                scale = min(dr, dg, db)
                if scale == 0:
                    self.action['on_draw'] = lambda *args: None
            self.rectangle.color = (
                self.rectangle.color[0] + 5*min(int(dr / scale), 1),
                self.rectangle.color[1] + 5*min(int(dg / scale), 1),
                self.rectangle.color[2] + 5*min(int(db / scale), 1)
            )
            return 1
        self.action['on_draw'] = lambda *args: None

    def on_hover(self: Button):
        if not self.in_:
            self.text2.visible = True
            self.action['on_draw'] = lambda self: change_color_to(self, self.secondary_color)
            self.in_ = True

    def on_out(self: Button):
        if self.in_:
            self.text2.visible = False
            self.action['on_draw'] = lambda self: change_color_to(self, self.primary_color)
            self.in_ = False

    button.action['on_hover'] = on_hover
    button.action['on_out'] = on_out
    return button


class MainMenu(BaseForm):
    """ The first state the user sees """
    def __init__(self, window: Main):
        super().__init__(window)
        self.caption = 'musicality - Main Menu'

        self.elements = []  # type: List[UIElement]

        exit_button = create_menu_button('Exit', 'See you later')
        exit_button.action['on_press'] = lambda *args: self.on_close()
        exit_button.position = self.width//2, self.height-762

        options_button = create_menu_button('Options', 'Change settings')
        # options_button.action['on_press'] = self.on_close
        options_button.position = self.width//2, self.height-616

        edit_button = create_menu_button('Edit', 'Make your own level!')
        # edit_button.action['on_press'] = self.on_close
        edit_button.position = self.width//2, self.height-470

        start_button = create_menu_button('Start', 'Select songs to play!')
        start_button.action['on_press'] = lambda *args: self.change_state('song select')
        start_button.position = self.width//2, self.height-324

        self.elements.extend((exit_button, options_button, edit_button, start_button))

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
            elif element.in_:
                element.on_out()

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

