from pathlib import Path

import arcade

from game.window.window import BaseForm, Main
from game.window import key
from game.graphics import UIElement, Sprite, DrawableRectangle, Group, Text
from game.audio import Audio
from game.animation.ease import ColorChange, Move


def create_back_button(text: str, color=arcade.color.ROSE_BONBON, secondary_color=arcade.color.RED_VIOLET):
    """ Create a back button that moves when hover """
    drawable = Group([])
    button = UIElement(drawable=drawable)

    # button.primary_color, button.secondary_color = color, secondary_color

    button.main_rec = main_rec = DrawableRectangle(0, 0, 190, 64, color)
    button.part_rec = part_rec = DrawableRectangle(0, 0, 86, 64, color)
    button.text = text_ = Text(text, 0, 0, arcade.color.WHITE, 26, anchor_y='center')
    button.symbol = symbol = Sprite('resources/images/button back symbol.png')

    p1, p2, p3, p4 = (35, 50), (3, 50), (20, 50), (57, 50)
    q1, q2, q3, q4 = (95, 50), (43, 50), (36, 50), (117, 50)

    main_rec.position, part_rec.position, symbol.position, text_.position = p1, p2, p3, p4
    drawable.extend((main_rec, part_rec, symbol, text_))

    color_change = ColorChange(duration=0.5)

    def change(self, color1, color2):
        try:
            self.part_rec.rgba = color_change(color1=color1, color2=color2)
        except TimeoutError:
            raise
        except AssertionError as e:
            raise TimeoutError from e

    eased_move = Move(duration=0.5)

    def move(self, forward: bool):
        if forward:
            try:
                x, y = eased_move(posn1=p1, posn2=q1)
                self.main_rec.position = [x, y]
                x, y = eased_move(posn1=p2, posn2=q2)
                self.part_rec.position = [x, y]
                x, y = eased_move(posn1=p3, posn2=q3)
                self.symbol.position = [x, y]
                x, y = eased_move(posn1=p4, posn2=q4)
                self.text.position = [x, y]
            except TimeoutError:
                raise
        else:
            try:
                x, y = eased_move(posn1=q1, posn2=p1)
                self.main_rec.position = [x, y]
                x, y = eased_move(posn1=q2, posn2=p2)
                self.part_rec.position = [x, y]
                x, y = eased_move(posn1=q3, posn2=p3)
                self.symbol.position = [x, y]
                x, y = eased_move(posn1=q4, posn2=p4)
                self.text.position = [x, y]
            except TimeoutError:
                raise

    from pathlib import Path
    hover_sound = Audio(filepath=Path('resources/sound/menu hover.wav'), absolute=False, static=True)

    def on_in(self: UIElement):
        assert not self.in_
        hover_sound.play(force=True)
        color_change.begin()
        eased_move.begin()
        try:
            self.remove_action('on_draw', 1)
        except IndexError:
            pass
        self.add_action('on_draw', lambda self: (change(self, color1=color, color2=secondary_color), move(self, forward=True)), 1)

    def on_out(self):
        assert self.in_
        color_change.begin()
        eased_move.begin()
        eased_move.begin()
        try:
            self.remove_action('on_draw', 1)
        except IndexError:
            pass
        self.add_action('on_draw', lambda self: (change(self, color1=secondary_color, color2=color), move(self, forward=False)), 1)

    button.add_action('on_in', on_in, 1)
    button.add_action('on_out', on_out, 2)
    return button


class SongSelect(BaseForm):
    """ Screen player can select songs """
    def __init__(self, window: Main):
        super().__init__(window)
        self.caption = 'musicality - Song Select'

        self.elements = []  # type: List[UIElement]

        backward_sound = Audio(filepath=Path('resources/sound/menu press backward.wav'), absolute=False)
        back_button = create_back_button('back')
        back_button.add_action('on_press', lambda *args: (backward_sound.play(), self.change_state('main menu')))

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

