from typing import List
from pathlib import Path

import arcade

from game.window.window import BaseForm, Main
from game.graphics.element import Button, UIElement, Text
from game.animation.ease import EaseColor
from game.legacy.audio import Audio


def create_menu_button(text1: str, text2: str = '', color=arcade.color.PURPLE_HEART, secondary_color=arcade.color.RED_VIOLET):
    """ Create a menu button that changes color when hover """
    color = color[0], color[1], color[2], 230
    secondary_color = secondary_color[0], secondary_color[1], secondary_color[2], 230
    button = Button(0, 0, 550, 120, color, secondary_color=secondary_color, alpha=230)
    text1_ = Text(text1, button.left+140, button.bottom+42, arcade.color.WHITE, 56)
    text2_ = Text(text2, button.left+180, button.bottom+16, arcade.color.WHITE, 16)
    text2_.visible = False
    button.text = text1_
    button.text2 = text2_
    button.drawable.append(text2_)

    color_change = EaseColor(duration=0.25)

    def change(self: Button, color1, color2):
        try:
            self.rectangle.rgba = color_change(color1=color1, color2=color2)
        except TimeoutError:
            raise

    hover_sound = Audio(filepath=Path('resources/sound/menu hover.wav'), absolute=False)

    def change_to_secondary_color(self):
        change(self, self.primary_color, self.secondary_color)

    def change_to_primary_color(self):
        change(self, self.secondary_color, self.primary_color)

    def on_in(self: Button):
        try:
            self.remove_action('on_draw', 2)
        except IndexError:
            pass
        try:
            assert not self.in_, 'called while already in'
            hover_sound.play(force=True)
            color_change.begin()
            self.add_action('on_draw', change_to_secondary_color, 1)
            self.text2.visible = True
        except AssertionError as e:
            raise TimeoutError from e

    def on_out(self: Button):
        try:
            self.remove_action('on_draw', 1)
        except IndexError:
            pass
        try:
            assert self.in_, 'called while already out'
            color_change.begin()
            self.add_action('on_draw', change_to_primary_color, 2)
            self.text2.visible = False
        except AssertionError as e:
            raise TimeoutError from e

    button.add_action('on_in', on_in, 3)
    button.add_action('on_out', on_out, 4)
    return button


class MainMenu(BaseForm):
    """ The first state the user sees """
    def __init__(self, window: Main):
        super().__init__(window)
        self.caption = 'musicality - Main Menu'

        self.elements = []  # type: List[UIElement]

        from threading import Timer

        delayed_close = Timer(0.5, self.on_close)  # 1.5

        backward_sound = Audio(filepath=Path('resources/sound/menu press backward.wav'), absolute=False)
        exit_button = create_menu_button('Exit', 'See you later')
        exit_button.add_action('on_press', lambda *args: (backward_sound.play(), delayed_close.start()))
        exit_button.position = self.width//2, self.height-762

        sound = Audio(filepath=Path('resources/sound/menu press options.wav'), absolute=False)
        options_button = create_menu_button('Options', 'Change settings')
        options_button.add_action('on_press', lambda *args: (sound.play(), ))
        options_button.position = self.width//2, self.height-616

        sound1 = sound.clone()
        edit_button = create_menu_button('Edit', 'Make your own level!')
        edit_button.add_action('on_press', lambda *args: (sound1.play(), ))
        edit_button.position = self.width//2, self.height-470

        sound2 = Audio(filepath=Path('resources/sound/menu press start.wav'), absolute=False)
        start_button = create_menu_button('Start', 'Select songs to play!')
        start_button.add_action('on_press', lambda *args: (sound2.play(), self.change_state('song select')))
        start_button.position = self.width//2, self.height-324

        self.elements.extend((exit_button, options_button, edit_button, start_button))

    def on_draw(self):
        self.clear()
        # DRAW BG
        if self._window._handler_cache['song select'].bg:
            self._window._handler_cache['song select'].bg.draw()
        # DRAW UI
        for element in self.elements:
            element.draw()

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        # UI MANAGEMENT
        for element in self.elements:
            if element.is_inside(x, y):
                element.on_hover()
                if not element.in_:
                    element.on_in()
            elif element.in_:
                element.on_out()

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == 1:
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
            self._window.change_handler(state)

