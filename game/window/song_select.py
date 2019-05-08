from pathlib import Path

import arcade

from game.window.window import BaseForm, Main
from game.window import key
from game.graphics.text import Text
from game.graphics.primitives import UIElement, Sprite, DrawableRectangle, Group
from game.audio import Audio
from game.animation.ease import ColorChange, Move


def create_back_button(text: str, color=arcade.color.ROSE_BONBON, secondary_color=arcade.color.RED_VIOLET):
    """ Create a back button that moves when hover """
    drawable = Group([])
    button = UIElement(drawable=drawable)

    # button.primary_color, button.secondary_color = color, secondary_color

    button.main_rec = main_rec = DrawableRectangle(0, 0, 190, 64, color)
    button.part_rec = part_rec = DrawableRectangle(0, 0, 86, 64, arcade.color.RED_DEVIL)
    drawable.extend((main_rec, part_rec))
    part_rec.left = main_rec.left
    main_rec.move(-60, 0)
    part_rec.move(-40, 0)
    button.position = 95 - 60, 0
    button.text = text_ = Text(text, 57, main_rec.position[1], arcade.color.WHITE, 26, anchor_y='center')
    button.symbol = symbol = Sprite('resources/images/button back symbol.png')
    symbol.position = list(part_rec.position)
    symbol.left = 4

    drawable.extend((symbol, text_))
    button.position = button.position[0], 50

    color_change = ColorChange(duration=0.25)

    def change(self, color1, color2):
        try:
            self.part_rec.rgba = color_change(color1=color1, color2=color2)
        except TimeoutError:
            pass
        except AssertionError:
            pass

    eased_move = Move(duration=0.5)

    a = main_rec.position
    b = part_rec.position
    c = symbol.position
    d = text_.position

    def move(self, forward=1):
        try:
            dx, dy = eased_move(posn1=a, posn2=(a[0] + forward*60, a[1]))
            self.main_rec.position = [dx, dy]
            dx, dy = eased_move(posn1=b, posn2=(b[0] + forward*40, b[1]))
            self.part_rec.position = [dx, dy]
            dx, dy = eased_move(posn1=c, posn2=(c[0] + forward*17, c[1]))
            self.symbol.position = [dx, dy]
            dx, dy = eased_move(posn1=d, posn2=(d[0] + forward*48, d[1]))
            self.text.position = [dx, dy]
        except TimeoutError:
            self.action['on_draw'] = None

    from pathlib import Path
    hover_sound = Audio(filepath=Path('resources/sound/menu hover.wav'), absolute=False, static=True)

    def on_in(self):
        assert not self.in_
        hover_sound.play(force=True)
        color_change.begin()
        eased_move.begin()
        self.action['on_draw'] = lambda self: (change(self, color1=color, color2=secondary_color), move(self, forward=1))
        self.in_ = True

    def on_out(self):
        assert self.in_
        color_change.begin()
        eased_move.begin()
        self.action['on_draw'] = lambda self: (change(self, color1=secondary_color, color2=color), move(self, forward=-1))
        self.in_ = False

    button.action['on_in'] = on_in
    button.action['on_out'] = on_out
    return button


class SongSelect(BaseForm):
    """ Screen player can select songs """
    def __init__(self, window: Main):
        super().__init__(window)
        self.caption = 'musicality - Song Select'

        self.elements = []  # type: List[UIElement]

        backward_sound = Audio(filepath=Path('resources/sound/menu press backward.wav'), absolute=False)
        back_button = create_back_button('back')
        back_button.action['on_press'] = lambda *args: (backward_sound.play(), self.change_state('main menu'))

        self.elements.append(back_button)

    def on_draw(self):
        self.clear()
        # DRAW UI
        for element in self.elements:
            element.draw()

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.ESCAPE:
            self.change_state('main menu')

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

    def on_text(self, text: str):
        pass

    def change_state(self, state: str):
        if state == 'main menu':
            from .main_menu import MainMenu
            self._window.change_handler(MainMenu(self._window))
        elif state == 'game':
            pass

