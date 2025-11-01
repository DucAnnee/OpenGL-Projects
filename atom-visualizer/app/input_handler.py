import glfw
import imgui
import numpy as np
from lib.camera import Camera
from objects.atom import Atom
from objects.colors import Color


class InputHandler:
    """Handles all keyboard and mouse input for the viewer"""

    def __init__(self, viewer):
        self.viewer = viewer
        self._dragging = False
        self._last_pos = (0, 0)

    def setup_callbacks(self, window):
        glfw.set_key_callback(window, self.on_key)
        glfw.set_cursor_pos_callback(window, self.on_mouse_move)
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_scroll_callback(window, self.on_mouse_scroll)
        glfw.set_char_callback(window, self.on_char)

    def on_char(self, win, char):
        self.viewer.gui.impl.char_callback(win, char)

    def on_key(self, win, key, scancode, action, mods):
        # fmt: off
        self.viewer.gui.impl.keyboard_callback(win, key, scancode, action, mods)

        io = imgui.get_io()
        if io.want_capture_keyboard:
            return

        if action == glfw.PRESS or action == glfw.REPEAT:
            # quit
            if key == glfw.KEY_ESCAPE or (key == glfw.KEY_Q and (mods & glfw.MOD_CONTROL)):
                glfw.set_window_should_close(win, True)
                return

            # change mode
            if key == glfw.KEY_A and action == glfw.PRESS and (mods & glfw.MOD_CONTROL):
                self.viewer.scene.set_current_atom(self.viewer.scene.get_current_atom())
                self.viewer.rendering_mode = "atom"
                self.viewer.camera = Camera(distance=10)
                return
            if key == glfw.KEY_M and action == glfw.PRESS and (mods & glfw.MOD_CONTROL):
                self.viewer.scene.set_current_molecule(self.viewer.scene.get_current_molecule())
                self.viewer.rendering_mode = "molecule"
                self.viewer.camera = Camera(distance=10)
                return

            # object selection
            if key == glfw.KEY_TAB and action == glfw.PRESS:
                if mods & glfw.MOD_SHIFT:
                    self.viewer.scene.select_previous()
                else:
                    self.viewer.scene.select_next()
                selected = self.viewer.scene.get_selected()
                if selected:
                    print(f"Selected: {selected.name}")
                return

    def on_mouse_button(self, win, button, action, mods):
        self.viewer.gui.impl.mouse_callback(win, button, action, mods)

        io = imgui.get_io()
        if io.want_capture_mouse:
            return

        if action == glfw.PRESS:
            self._last_pos = glfw.get_cursor_pos(win)

            if button == glfw.MOUSE_BUTTON_LEFT and not (mods & glfw.MOD_SHIFT):
                self._dragging = True  # orbit
        else:
            self._dragging = False

    def on_mouse_move(self, win, x, y):
        io = imgui.get_io()
        if io.want_capture_mouse:
            return

        if not self._dragging:
            return

        cur = (x, y)
        old = self._last_pos
        self._last_pos = cur

        if self._dragging:
            self.viewer.camera.drag(
                np.array(old, dtype=np.float32),
                np.array(cur, dtype=np.float32),
                np.array(self.viewer.size, dtype=np.float32),
            )

    def on_mouse_scroll(self, win, xoff, yoff):
        self.viewer.gui.impl.scroll_callback(win, xoff, yoff)

        io = imgui.get_io()
        if io.want_capture_mouse:
            return

        self.viewer.camera.zoom(yoff, self.viewer.size[1])  # wheel up to zoom in
