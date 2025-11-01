import glfw
import imgui
import numpy as np


class InputHandler:
    """Handles all keyboard and mouse input for the viewer"""

    def __init__(self, viewer):
        self.viewer = viewer
        self._dragging = False
        self._panning = False
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
        self.viewer.gui.impl.keyboard_callback(win, key, scancode, action, mods)

        io = imgui.get_io()
        if io.want_capture_keyboard:
            return

        if action == glfw.PRESS or action == glfw.REPEAT:
            # quit
            if key == glfw.KEY_ESCAPE or (
                key == glfw.KEY_Q and (mods & glfw.MOD_CONTROL)
            ):
                glfw.set_window_should_close(win, True)
                return

            # toggle wireframe
            if key == glfw.KEY_W and action == glfw.PRESS and (mods & glfw.MOD_CONTROL):
                self.viewer.rendering_mode = "wireframe"
                return
            if key == glfw.KEY_F and action == glfw.PRESS and (mods & glfw.MOD_CONTROL):
                self.viewer.rendering_mode = "flat"
                return
            if key == glfw.KEY_P and action == glfw.PRESS and (mods & glfw.MOD_CONTROL):
                self.viewer.rendering_mode = "phong"
                return
            if key == glfw.KEY_G and action == glfw.PRESS and (mods & glfw.MOD_CONTROL):
                self.viewer.rendering_mode = "gouraud"
                return
            if key == glfw.KEY_T and action == glfw.PRESS and (mods & glfw.MOD_CONTROL):
                self.viewer.rendering_mode = "texture"
                return

            # toggle manipulation mode
            if key == glfw.KEY_M and action == glfw.PRESS:
                self.viewer.manipulation_mode = (
                    "object" if self.viewer.manipulation_mode == "camera" else "camera"
                )
                print(f"Mode: {self.viewer.manipulation_mode.upper()}")
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

            # delete selected object
            if key == glfw.KEY_DELETE and action == glfw.PRESS:
                if self.viewer.scene.selected_index is not None:
                    self.viewer.scene.remove(self.viewer.scene.selected_index)
                    print("Object deleted")
                return

            if (
                self.viewer.manipulation_mode == "object"
                and self.viewer.scene.get_selected()
            ):
                # Translation
                if key == glfw.KEY_LEFT:
                    self.viewer.scene.manipulate_selected("translate_x", -0.1)
                elif key == glfw.KEY_RIGHT:
                    self.viewer.scene.manipulate_selected("translate_x", 0.1)
                elif key == glfw.KEY_UP:
                    self.viewer.scene.manipulate_selected("translate_z", -0.1)
                elif key == glfw.KEY_DOWN:
                    self.viewer.scene.manipulate_selected("translate_z", 0.1)
                elif key == glfw.KEY_E:
                    self.viewer.scene.manipulate_selected("translate_y", 0.1)
                elif key == glfw.KEY_Q:
                    self.viewer.scene.manipulate_selected("translate_y", -0.1)

                # Reset
                elif key == glfw.KEY_0 or key == glfw.KEY_KP_0:
                    self.viewer.scene.manipulate_selected("reset")
                    print("Transform reset")

    def on_mouse_button(self, win, button, action, mods):
        self.viewer.gui.impl.mouse_callback(win, button, action, mods)

        io = imgui.get_io()
        if io.want_capture_mouse:
            return

        if action == glfw.PRESS:
            self._last_pos = glfw.get_cursor_pos(win)

            if button == glfw.MOUSE_BUTTON_LEFT and not (mods & glfw.MOD_SHIFT):
                self._dragging = True  # orbit
            if button == glfw.MOUSE_BUTTON_RIGHT or (
                button == glfw.MOUSE_BUTTON_LEFT and (mods & glfw.MOD_SHIFT)
            ):
                self._panning = True  # pan
        else:
            self._dragging = False
            self._panning = False

    def on_mouse_move(self, win, x, y):
        io = imgui.get_io()
        if io.want_capture_mouse:
            return

        if not (self._dragging or self._panning):
            return

        cur = (x, y)
        old = self._last_pos
        self._last_pos = cur

        if self._dragging:
            if self.viewer.manipulation_mode == "camera":
                # orbit: use trackball drag with window size
                self.viewer.camera.drag(
                    np.array(old, dtype=np.float32),
                    np.array(cur, dtype=np.float32),
                    np.array(self.viewer.size, dtype=np.float32),
                )
            else:
                # object rotation
                selected = self.viewer.scene.get_selected()
                if selected:
                    selected.drag(
                        np.array(old, dtype=np.float32),
                        np.array(cur, dtype=np.float32),
                        np.array(self.viewer.size, dtype=np.float32),
                    )
        elif self._panning:
            # pan in camera space
            self.viewer.camera.pan(
                np.array(old, dtype=np.float32), np.array(cur, dtype=np.float32)
            )

    def on_mouse_scroll(self, win, xoff, yoff):
        self.viewer.gui.impl.scroll_callback(win, xoff, yoff)

        io = imgui.get_io()
        if io.want_capture_mouse:
            return

        self.viewer.camera.zoom(yoff, self.viewer.size[1])  # wheel up to zoom in
