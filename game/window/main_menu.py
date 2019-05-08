from typing import List
from pathlib import Path

import arcade

from game.window.window import BaseForm, Main
from game.window import key
from game.graphics.element import Button, UIElement, Text
from game.animation.ease import ColorChange
from game.audio import Audio


def create_menu_button(text1: str, text2: str = '', color=arcade.color.PURPLE_HEART, secondary_color=arcade.color.RED_VIOLET):
    """ Create a menu button that changes color when hover """
    button = Button(0, 0, 550, 120, color, secondary_color=secondary_color)
    text1_ = Text(text1, button.left+140, button.bottom+42, arcade.color.WHITE, 56)
    text2_ = Text(text2, button.left+180, button.bottom+16, arcade.color.WHITE, 16)
    text2_.visible = False
    button.text = text1_
    button.text2 = text2_
    button.drawable.append(text2_)

    color_change = ColorChange(duration=0.25)

    def change(self: Button, color1, color2):
        try:
            self.rectangle.rgba = color_change(color1=color1, color2=color2)
        except TimeoutError:
            self.action['on_draw'] = None

    from pathlib import Path
    hover_sound = Audio(filepath=Path('resources/sound/menu hover.wav'), absolute=False, static=True)

    def on_in(self: Button):
        assert not self.in_
        hover_sound.play(force=True)
        color_change.begin()
        self.action['on_draw'] = lambda self: change(self, self.primary_color, self.secondary_color)
        self.text2.visible = True
        self.in_ = True

    def on_out(self: Button):
        assert self.in_
        color_change.begin()
        self.action['on_draw'] = lambda self: change(self, self.secondary_color, self.primary_color)
        self.text2.visible = False
        self.in_ = False

    button.action['on_in'] = on_in
    button.action['on_out'] = on_out
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
        exit_button.action['on_press'] = lambda *args: (backward_sound.play(), delayed_close.start())
        exit_button.position = self.width//2, self.height-762

        sound = Audio(filepath=Path('resources/sound/menu press options.wav'), absolute=False)
        options_button = create_menu_button('Options', 'Change settings')
        options_button.action['on_press'] = lambda *args: sound.play()
        options_button.position = self.width//2, self.height-616

        sound1 = sound.clone()
        edit_button = create_menu_button('Edit', 'Make your own level!')
        edit_button.action['on_press'] = lambda *args: sound1.play()
        edit_button.position = self.width//2, self.height-470

        sound2 = Audio(filepath=Path('resources/sound/menu press start.wav'), absolute=False)
        start_button = create_menu_button('Start', 'Select songs to play!')
        start_button.action['on_press'] = lambda *args: (sound2.play(), self.change_state('song select'))
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

