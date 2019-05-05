from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Optional
from functools import partial

import pyglet

glClear = partial(pyglet.gl.glClear, pyglet.gl.GL_COLOR_BUFFER_BIT | pyglet.gl.GL_DEPTH_BUFFER_BIT)


class BaseWindow(metaclass=ABCMeta):
    """ Base window for each state handling arcade.Window """

    __slots__ = '_window'

    def __init__(self, window: pyglet.window.Window):
        self._window = window

    @abstractmethod
    def on_key_press(self, symbol: int, modifiers: int):
        pass

    @abstractmethod
    def on_key_release(self, symbol: int, modifiers: int):
        pass

    @abstractmethod
    def on_text(self, text: str):
        """The user input some text.

        Typically this is called after :py:meth:`~pyglet.window.Window.on_key_press` and before
        :py:meth:`~pyglet.window.Window.on_key_release`, but may also be called multiple times if the key
        is held down (key repeating); or called without key presses if
        another input method was used (e.g., a pen input).

        You should always use this method for interpreting text, as the
        key symbols often have complex mappings to their unicode
        representation which this event takes care of.

        :Parameters:
            `text` : unicode
                The text entered by the user.

        :event:
        """
        pass

    def on_text_motion(self, motion: int):
        """The user moved the text input cursor.

        Typically this is called after :py:meth:`~pyglet.window.Window.on_key_press` and before
        :py:meth:`~pyglet.window.Window.on_key_release`, but may also be called multiple times if the key
        is help down (key repeating).

        You should always use this method for moving the text input cursor
        (caret), as different platforms have different default keyboard
        mappings, and key repeats are handled correctly.

        The values that `motion` can take are defined in
        :py:mod:`pyglet.window.key`:

        * MOTION_UP
        * MOTION_RIGHT
        * MOTION_DOWN
        * MOTION_LEFT
        * MOTION_NEXT_WORD
        * MOTION_PREVIOUS_WORD
        * MOTION_BEGINNING_OF_LINE
        * MOTION_END_OF_LINE
        * MOTION_NEXT_PAGE
        * MOTION_PREVIOUS_PAGE
        * MOTION_BEGINNING_OF_FILE
        * MOTION_END_OF_FILE
        * MOTION_BACKSPACE
        * MOTION_DELETE

        :Parameters:
            `motion` : int
                The direction of motion; see remarks.

        :event:
        """
        pass

    def on_text_motion_select(self, motion: int):
        """The user moved the text input cursor while extending the
        selection.

        Typically this is called after :py:meth:`~pyglet.window.Window.on_key_press` and before
        :py:meth:`~pyglet.window.Window.on_key_release`, but may also be called multiple times if the key
        is help down (key repeating).

        You should always use this method for responding to text selection
        events rather than the raw :py:meth:`~pyglet.window.Window.on_key_press`, as different platforms
        have different default keyboard mappings, and key repeats are
        handled correctly.

        The values that `motion` can take are defined in :py:mod:`pyglet.window.key`:

        * MOTION_UP
        * MOTION_RIGHT
        * MOTION_DOWN
        * MOTION_LEFT
        * MOTION_NEXT_WORD
        * MOTION_PREVIOUS_WORD
        * MOTION_BEGINNING_OF_LINE
        * MOTION_END_OF_LINE
        * MOTION_NEXT_PAGE
        * MOTION_PREVIOUS_PAGE
        * MOTION_BEGINNING_OF_FILE
        * MOTION_END_OF_FILE

        :Parameters:
            `motion` : int
                The direction of selection motion; see remarks.

        :event:
        """
        pass

    @abstractmethod
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        pass

    @abstractmethod
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        pass

    @abstractmethod
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        pass

    @abstractmethod
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        pass

    @abstractmethod
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        """The mouse wheel was scrolled.

        Note that most mice have only a vertical scroll wheel, so
        `scroll_x` is usually 0.  An exception to this is the Apple Mighty
        Mouse, which has a mouse ball in place of the wheel which allows
        both `scroll_x` and `scroll_y` movement.

        :Parameters:
            `x` : int
                Distance in pixels from the left edge of the window.
            `y` : int
                Distance in pixels from the bottom edge of the window.
            `scroll_x` : int
                Number of "clicks" towards the right (left if negative).
            `scroll_y` : int
                Number of "clicks" upwards (downwards if negative).

        :event:
        """
        pass

    def on_close(self):
        """The user attempted to close the window.

        This event can be triggered by clicking on the "X" control box in
        the window title bar, or by some other platform-dependent manner.

        The default handler sets `has_exit` to ``True``.  In pyglet 1.1, if
        `pyglet.app.event_loop` is being used, `close` is also called,
        closing the window immediately.

        :event:
        """
        pass

    def on_mouse_enter(self, x: int, y: int):
        """The mouse was moved into the window.

        This event will not be triggered if the mouse is currently being
        dragged.

        :Parameters:
            `x` : int
                Distance in pixels from the left edge of the window.
            `y` : int
                Distance in pixels from the bottom edge of the window.

        :event:
        """
        pass

    def on_mouse_leave(self, x: int, y: int):
        """The mouse was moved outside of the window.

        This event will not be triggered if the mouse is currently being
        dragged.  Note that the coordinates of the mouse pointer will be
        outside of the window rectangle.

        :Parameters:
            `x` : int
                Distance in pixels from the left edge of the window.
            `y` : int
                Distance in pixels from the bottom edge of the window.

        :event:
        """
        pass

    def on_expose(self):
        """A portion of the window needs to be redrawn.

        This event is triggered when the window first appears, and any time
        the contents of the window is invalidated due to another window
        obscuring it.

        There is no way to determine which portion of the window needs
        redrawing.  Note that the use of this method is becoming
        increasingly uncommon, as newer window managers composite windows
        automatically and keep a backing store of the window contents.

        :event:
        """
        pass

    def on_resize(self, width: int, height: int):
        """The window was resized.

        The window will have the GL context when this event is dispatched;
        there is no need to call `switch_to` in this handler.

        :Parameters:
            `width` : int
                The new width of the window, in pixels.
            `height` : int
                The new height of the window, in pixels.

        :event:
        """
        pass

    def on_move(self, x: int, y: int):
        """The window was moved.

        :Parameters:
            `x` : int
                Distance from the left edge of the screen to the left edge
                of the window.
            `y` : int
                Distance from the top edge of the screen to the top edge of
                the window.  Note that this is one of few methods in pyglet
                which use a Y-down coordinate system.

        :event:
        """
        pass

    def on_activate(self):
        """The window was activated.

        This event can be triggered by clicking on the title bar, bringing
        it to the foreground; or by some platform-specific method.

        When a window is "active" it has the keyboard focus.

        :event:
        """
        pass

    def on_deactivate(self):
        """The window was deactivated.

        This event can be triggered by clicking on another application
        window.  When a window is deactivated it no longer has the
        keyboard focus.

        :event:
        """
        pass

    def on_show(self):
        """The window was shown.

        This event is triggered when a window is restored after being
        minimised, or after being displayed for the first time.

        :event:
        """
        pass

    def on_hide(self):
        """The window was hidden.

        This event is triggered when a window is minimised or (on Mac OS X)
        hidden by the user.

        :event:
        """
        pass

    def on_context_lost(self):
        """The window's GL context was lost.

        When the context is lost no more GL methods can be called until it
        is recreated.  This is a rare event, triggered perhaps by the user
        switching to an incompatible video mode.  When it occurs, an
        application will need to reload all objects (display lists, texture
        objects, shaders) as well as restore the GL state.

        :event:
        """
        pass

    def on_context_state_lost(self):
        """The state of the window's GL context was lost.

        pyglet may sometimes need to recreate the window's GL context if
        the window is moved to another video device, or between fullscreen
        or windowed mode.  In this case it will try to share the objects
        (display lists, texture objects, shaders) between the old and new
        contexts.  If this is possible, only the current state of the GL
        context is lost, and the application should simply restore state.

        :event:
        """
        pass

    @abstractmethod
    def on_draw(self):
        """The window contents must be redrawn.

        The `EventLoop` will dispatch this event when the window
        should be redrawn.  This will happen during idle time after
        any window events and after any scheduled functions were called.

        The window will already have the GL context, so there is no
        need to call `switch_to`.  The window's `flip` method will
        be called after this event, so your event handler should not.

        You should make no assumptions about the window contents when
        this event is triggered; a resize or expose event may have
        invalidated the framebuffer since the last time it was drawn.

        .. versionadded:: 1.1

        :event:
        """
        pass

    # def update(self, delta_time: float):
    #     pass
    # removed due to redundancy: use on_update instead

    @abstractmethod
    def on_update(self, delta_time: float):
        pass

    @property
    def caption(self) -> str:
        """ The window caption (title) """
        return self._window.caption

    @property
    def resizeable(self) -> bool:
        """ True if the window is resizable """
        return self._window.resizeable

    @property
    def style(self) -> int:
        """ The window style; one of the ``WINDOW_STYLE_*`` constants """
        return self._window.style

    @property
    def fullscreen(self) -> bool:
        """ True if the window is currently fullscreen """
        return self._window.fullscreen

    @property
    def visible(self) -> bool:
        """ True if the window is currently visible """
        return self._window.visible

    @property
    def vsync(self) -> bool:
        """ True if vsync is on """
        return self._window.vsync

    @property
    def display(self):
        """ The display this window belongs to """
        return self._window.display

    @property
    def screen(self):
        """ The screen this window is fullscreen in """
        return self._window.screen

    @property
    def config(self) -> pyglet.gl.Config:
        """ A GL config describing the context of this window """
        return self._window.config

    @property
    def context(self) -> pyglet.gl.Context:
        """ The OpenGL context attached to this window """
        return self._window.context

    @property
    def width(self) -> int:
        """ The width of the window, in pixels """
        return self._window.width

    @width.setter
    def width(self, new_width: int):
        self._window.width = new_width

    @property
    def height(self) -> int:
        """ The height of the window, in pixels """
        return self._window.height

    @height.setter
    def height(self, new_height: int):
        self._window.height = new_height

    @property
    def projection(self) -> int:
        """ The height of the window, in pixels """
        return self._window.projection

    @projection.setter
    def projection(self, projection):
        self._window.projection = projection

    @caption.setter
    def caption(self, caption: str):
        """ The window caption (title) """
        self._window.caption = caption

    @property
    def size(self) -> (int, int):
        """Return the current size of the window.

        The window size does not include the border or title bar.

        :rtype: (int, int)
        :return: The width and height of the window, in pixels.
        """
        return self._window.get_size()

    @size.setter
    def size(self, size: (int, int)):
        """Resize the window.

        The behaviour is undefined if the window is not resizable, or if
        it is currently fullscreen.

        The window size does not include the border or title bar.

        :Parameters:
            `width` : int
                New width of the window, in pixels.
            `height` : int
                New height of the window, in pixels.
        """
        self._window.set_size(*size)

    @property
    def location(self) -> (int, int):
        """Return the current position of the window.

        :rtype: (int, int)
        :return: The distances of the left and top edges from their respective
            edges on the virtual desktop, in pixels.
        """
        return self._window.get_location()

    @location.setter
    def location(self, location: (int, int)):
        """Set the position of the window.

        :Parameters:
            `x` : int
                Distance of the left edge of the window from the left edge
                of the virtual desktop, in pixels.
            `y` : int
                Distance of the top edge of the window from the top edge of
                the virtual desktop, in pixels.

        """
        self._window.set_location(*location)

    def activate(self):
        """Attempt to restore keyboard focus to the window.

        Depending on the window manager or operating system, this may not
        be successful.  For example, on Windows XP an application is not
        allowed to "steal" focus from another application.  Instead, the
        window's taskbar icon will flash, indicating it requires attention.
        """
        self._window.activate()

    @visible.setter
    def visible(self, visible: bool = True):
        """ Show or hide the window """
        self._window.set_visible(visible)

    def minimize(self):
        """ Minimize the window """
        self._window.minimize()

    def maximize(self):
        """Maximize the window.

        The behaviour of this method is somewhat dependent on the user's
        display setup.  On a multi-monitor system, the window may maximize
        to either a single screen or the entire virtual desktop.
        """
        self._window.maximize()

    @vsync.setter
    def vsync(self, vsync: bool):
        """Enable or disable vertical sync control.

        When enabled, this option ensures flips from the back to the front
        buffer are performed only during the vertical retrace period of the
        primary display.  This can prevent "tearing" or flickering when
        the buffer is updated in the middle of a video scan.

        Note that LCD monitors have an analogous time in which they are not
        reading from the video buffer; while it does not correspond to
        a vertical retrace it has the same effect.

        Also note that with multi-monitor systems the secondary monitor
        cannot be synchronised to, so tearing and flicker cannot be avoided
        when the window is positioned outside of the primary display.

        :Parameters:
            `vsync` : bool
                If True, vsync is enabled, otherwise it is disabled.

        """
        self._window.set_vsync(vsync)

    def set_mouse_visible(self, visible: bool = True):
        """Show or hide the mouse cursor.

        The mouse cursor will only be hidden while it is positioned within
        this window.  Mouse events will still be processed as usual.

        :Parameters:
            `visible` : bool
                If True, the mouse cursor will be visible, otherwise it
                will be hidden.

        """
        self._window.set_mouse_visible(visible)

    def set_mouse_platform_visible(self, platform_visible: Optional[bool] = None):
        """Set the platform-drawn mouse cursor visibility.  This is called
        automatically after changing the mouse cursor or exclusive mode.

        Applications should not normally need to call this method, see
        `set_mouse_visible` instead.

        :Parameters:
            `platform_visible` : bool or None
                If None, sets platform visibility to the required visibility
                for the current exclusive mode and cursor type.  Otherwise,
                a bool value will override and force a visibility.

        """
        self._window.set_mouse_platform_visible(platform_visible)

    def set_mouse_cursor(self, cursor: Optional[pyglet.window.MouseCursor] = None):
        """Change the appearance of the mouse cursor.

        The appearance of the mouse cursor is only changed while it is
        within this window.

        :Parameters:
            `cursor` : `MouseCursor`
                The cursor to set, or None to restore the default cursor.

        """
        self._window.set_mouse_cursor(cursor)

    def set_exclusive_mouse(self, exclusive: bool = True):
        """Hide the mouse cursor and direct all mouse events to this
        window.

        When enabled, this feature prevents the mouse leaving the window.  It
        is useful for certain styles of games that require complete control of
        the mouse.  The position of the mouse as reported in subsequent events
        is meaningless when exclusive mouse is enabled; you should only use
        the relative motion parameters ``dx`` and ``dy``.

        :Parameters:
            `exclusive` : bool
                If True, exclusive mouse is enabled, otherwise it is disabled.

        """
        self._window.set_exclusive_mouse(exclusive)

    def set_exclusive_keyboard(self, exclusive: bool = True):
        """Prevent the user from switching away from this window using
        keyboard accelerators.

        When enabled, this feature disables certain operating-system specific
        key combinations such as Alt+Tab (Command+Tab on OS X).  This can be
        useful in certain kiosk applications, it should be avoided in general
        applications or games.

        :Parameters:
            `exclusive` : bool
                If True, exclusive keyboard is enabled, otherwise it is
                disabled.

        """
        self._window.set_exclusive_keyboard(exclusive)

    def get_system_mouse_cursor(self, name: str) -> pyglet.window.MouseCursor:
        """Obtain a system mouse cursor.

        Use `set_mouse_cursor` to make the cursor returned by this method
        active.  The names accepted by this method are the ``CURSOR_*``
        constants defined on this class.

        :Parameters:
            `name` : str
                Name describing the mouse cursor to return.  For example,
                ``CURSOR_WAIT``, ``CURSOR_HELP``, etc.

        :rtype: `MouseCursor`
        :return: A mouse cursor which can be used with `set_mouse_cursor`.
        """
        return self._window.get_system_mouse_cursor(name)

    def set_icon(self, *images: pyglet.image.AbstractImage):
        """Set the window icon.

        If multiple images are provided, one with an appropriate size
        will be selected (if the correct size is not provided, the image
        will be scaled).

        Useful sizes to provide are 16x16, 32x32, 64x64 (Mac only) and
        128x128 (Mac only).

        :Parameters:
            `images` : sequence of `pyglet.image.AbstractImage`
                List of images to use for the window icon.

        """
        self._window.set_icon(*images)

    # noinspection PyMethodMayBeStatic
    def clear(self):
        """Clear the window.

        This is a convenience method for clearing the color and depth
        buffer.  The window must be the active context (see `switch_to`).
        """
        glClear()

    @abstractmethod
    def change_state(self, state: str):
        """ Change state to `state` """
        raise NotImplementedError


class MainMenu(BaseWindow):
    """ The first state the user sees """
    def __init__(self, window: pyglet.window.Window):
        super().__init__(window)



