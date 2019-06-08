from __future__ import annotations

from pathlib import Path
from functools import partial

import arcade
import pyglet

from game.window.window import BaseForm, Main
from game.window import key
from game.graphics import UIElement, Sprite, DrawableRectangle, Group, Text, Rectangle
from game.animation.ease import EaseColor, EasePosition
from game.legacy.audio import Audio
from osu.beatmap import Beatmap, get_beatmaps

_beatmaps = get_beatmaps()


class Info(UIElement):
    def __init__(self):
        # rec = DrawableRectangle(0, 0, 50, 20)
        text = Text('Press Enter to play', 0, 0, arcade.color.WHITE, 12)
        drawable = Group([text])
        super().__init__(drawable=drawable)
        self.visible = False


class SongBar(UIElement):
    def __init__(self, beatmap: Beatmap, window: SongSelect, left=0, center_y=0):
        self.beatmap = beatmap
        rec = DrawableRectangle(0, 0, 960, 121, arcade.color.RED_VIOLET, 200)
        white_wash = DrawableRectangle(0, 0, 960, 121, arcade.color.WHITE, 50)
        white_wash.visible = False

        temp = Sprite(beatmap.background_filepath)
        pic_scale = 121 / temp.height
        pic = Sprite(beatmap.background_filepath, scale=pic_scale)
        pic.true_width, pic.true_height = temp.width, temp.height
        pic.bg_scale = max(1920 / pic.true_width, 1080 / pic.true_height)
        rec.left = left
        rec.center_y = center_y
        white_wash.position = rec.position
        pic.left = rec.left
        pic.center_y = rec.center_y

        title = Text(beatmap.title, pic.right + 21, rec.top - 32, arcade.color.WHITE, 24)
        artist_creator = Text(beatmap.artist + ' // ' + beatmap.creator, pic.right + 21, rec.top - 57,
                              arcade.color.WHITE, 19)
        version = Text(beatmap.version, pic.right + 21, rec.top - 82, arcade.color.WHITE, 19, bold=True)

        drawable = Group([])
        drawable.append(pic)
        drawable.append(rec)
        drawable.extend((title, artist_creator, version))
        drawable.append(white_wash)
        drawable.set_ref(index=1)
        rec_ref = Rectangle(rec.center_x, rec.center_y+6, rec.width, rec.height-12)
        super().__init__(drawable, ref_shape=rec_ref)
        self.rec, self.white_wash, self.pic, self.title, self.artist_creator, self.version = rec, white_wash, pic, title, artist_creator, version

        change_bg = partial(window.change_bg, Sprite(beatmap.background_filepath, pic.bg_scale, center_x=window.width // 2, center_y=window.height // 2))

        print((beatmap.title, beatmap.artist, beatmap.version))
        play = partial(window.play, beatmap.resource_loader.media(beatmap.audio_filename), beatmap.preview_timestamp)

        def on_in():
            if self.selected:
                window.show_info()

        def on_out(self):
            if self.selected:
                window.show_info(False)
            else:
                self.white_wash.visible = False

        self.add_action('on_press', lambda *args: (change_bg(), play()))
        self.add_action('on_in', lambda *args: (setattr(args[0].white_wash, 'visible', True), args[0].move(-50, 0), on_in()))
        self.add_action('on_out', lambda *args: (on_out(args[0]), args[0].move(50, 0)))
        self.add_action('on_select', lambda *args: (setattr(args[0].white_wash, 'visible', True), args[0].move(-100, 0)))
        self.add_action('on_unselect', lambda *args: (setattr(args[0].white_wash, 'visible', False), args[0].move(100, 0)))



class SlidingSongBar:

    # def create_song_bar(self, beatmap: Beatmap) -> UIElement:
    #     rec = DrawableRectangle(0, 0, 960, 64, arcade.color.RED_VIOLET, 200)

    def __init__(self, window: SongSelect):
        self.window = window
        self.song_bars = []
        self.on_screen = []
        self.selected = []

        hover_sound = Audio(filepath=Path('resources/sound/menu hover.wav'), absolute=False)

        overlap = 12
        pop = 100
        i = 0

        from threading import Timer

        print('loading beatmaps', end='')
        temp = [Timer(0.3+0.6*_, print, args=('.',), kwargs={'end': '',}) for _ in range(15)]

        for elem in temp:
            elem.start()

        for group in _beatmaps.values():
            bars = []
            for beatmap in group.values():
                song_bar = SongBar(beatmap, self.window, left=window.width // 2 + 200, center_y=self.window.height + i)
                song_bar.add_action('on_in', lambda *args: hover_sound.play())

                i -= song_bar.rec.height - overlap
                bars.append(song_bar)
            self.song_bars.append(bars)

        for elem in temp:
            elem.cancel()
        from random import random
        self.on_mouse_scroll(0, 0, 0, int(random()*-80))

    def get_selected(self) -> Beatmap:
        if self.selected:
            return self.selected[0].beatmap

    def on_draw(self):
        """ Draw what is on screen """
        for group in self.song_bars:
            for elem in group:
                if -200 < elem.position[1] < 1080+200:
                    elem.draw()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        # UI MANAGEMENT
        for group in self.song_bars:
            for element in group:
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
        for group in self.song_bars:
            for element in group:
                if element.is_inside(x, y):
                    if button == 1:
                        element.on_press()
                        if not element.selected:
                            element.on_select()
                            self.selected.append(element)
        temp = []
        for element in self.selected:
            if element.is_inside(x, y):
                pass
            else:
                element.on_unselect()
                temp.append(element)
        for elem in temp:
            self.selected.remove(elem)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        # UI MANAGEMENT
        for group in self.song_bars:
            for element in group:
                if element.pressed:
                    element.on_release()

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        # UI MANAGEMENT
        for group in self.song_bars:
            for element in group:
                element.move(0, -(120-12)*scroll_y)


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

    color_change = EaseColor(duration=0.5)

    def change(self, color1, color2):
        try:
            self.part_rec.rgba = color_change(color1=color1, color2=color2)
        except TimeoutError:
            raise
        except AssertionError as e:
            raise TimeoutError from e

    eased_move = EasePosition(duration=0.3)

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

    hover_sound = Audio(filepath=Path('resources/sound/menu hover.wav'), absolute=False)

    def on_in(self: UIElement):
        assert not self.in_
        hover_sound.play(force=True)
        color_change.begin()
        eased_move.begin()
        try:
            self.remove_action('on_draw', 1)
        except IndexError:
            pass
        self.add_action('on_draw',
                        lambda self: (change(self, color1=color, color2=secondary_color), move(self, forward=True)), 1)

    def on_out(self):
        assert self.in_
        color_change.begin()
        eased_move.begin()
        eased_move.begin()
        try:
            self.remove_action('on_draw', 1)
        except IndexError:
            pass
        self.add_action('on_draw',
                        lambda self: (change(self, color1=secondary_color, color2=color), move(self, forward=False)), 1)

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

        self.bar_manager = SlidingSongBar(self)

        self.bg = None
        self.player = None

        self.bar_manager.on_mouse_press(1800, self.width//2, 1, 0)
        self.bar_manager.on_mouse_press(0, 1080, 2, 0)

        self.info = Info()
        self.elements.append(self.info)

    def change_bg(self, new_bg: Sprite):
        self.bg = new_bg

    def play(self, audio_source: 'pyglet.media.Source', timestamp: float = 0):
        if not self.player:
            import pyglet
            self.player = pyglet.media.Player()
        if self.player.playing:
            self.player.queue(audio_source)
            self.player.next_source()
            self.player.seek(timestamp)
            self.player.play()
        else:
            self.player.queue(audio_source)
            self.player.seek(timestamp)
            self.player.play()

    def get_selected(self) -> Beatmap:
        return self.bar_manager.get_selected()

    def on_draw(self):
        self.clear()
        # DRAW GRAPHICS
        if self.bg:
            self.bg.draw()
        # DRAW UI
        self.bar_manager.on_draw()
        for element in self.elements:
            element.draw()

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.ESCAPE:
            self.change_state('main menu')
        elif symbol in (key.ENTER, key.SPACE):
            selected_beatmap = self.get_selected()
            if selected_beatmap:
                self.change_state('game', selected_beatmap)

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.info.position = x, y
        # UI MANAGEMENT
        for element in self.elements:
            if element.is_inside(x, y):
                element.on_hover()
                if not element.in_:
                    element.on_in()
            elif element.in_:
                element.on_out()

        self.bar_manager.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == 1:
            # UI MANAGEMENT
            for element in self.elements:
                if element.is_inside(x, y):
                    element.on_press()

        self.bar_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        # UI MANAGEMENT
        for element in self.elements:
            if element.pressed:
                element.on_release()

        self.bar_manager.on_mouse_release(x, y, button, modifiers)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.bar_manager.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_text(self, text: str):
        pass

    def change_state(self, state: str, *args):
        if state == 'main menu':
            self._window.change_handler(state)
        elif state == 'game':
            self.player.next_source()
            self._window.change_handler(state, *args)

    def show_info(self, arg=True):
        if arg:
            self.info.visible = True
        else:
            self.info.visible = False
