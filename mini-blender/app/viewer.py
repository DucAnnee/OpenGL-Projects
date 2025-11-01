import OpenGL.GL as GL
import numpy as np
import glfw
import imgui

from lib.camera import Camera
from lib.transform import identity
from objects.abstract import Drawable
from app.grid import Grid
from app.scene_manager import SceneManager
from app.gui import GUI
from app.input_handler import InputHandler


# ------------  Viewer class & windows management ------------------------------
class Viewer:
    """GLFW viewer windows, with classic initialization & graphics loop"""

    def __init__(self, width=300, height=800):

        # version hints: create GL windows with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, True)
        glfw.window_hint(glfw.SCALE_TO_MONITOR, True)
        self.win = glfw.create_window(width, height, "Viewer", None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        def framebuffer_size_callback(window, width, height):
            self.size = (width, height)
            GL.glViewport(0, 0, width, height)

        glfw.set_framebuffer_size_callback(self.win, framebuffer_size_callback)

        # useful message to check OpenGL renderer characteristics
        print(
            "OpenGL",
            GL.glGetString(GL.GL_VERSION).decode() + ", GLSL",
            GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() + ", Renderer",
            GL.glGetString(GL.GL_RENDERER).decode(),
        )

        GL.glViewport(0, 0, width, height)
        GL.glClearColor(0.18, 0.18, 0.18, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        # GL.glEnable(GL.GL_CULL_FACE)
        GL.glLineWidth(1.0)

        # initially empty list of object to draw
        self.grid = Grid().setup()
        self.display_grid = True
        self.scene = SceneManager()

        # camera setup
        self.size = (width, height)
        self.camera = Camera.place(
            eye=np.array([4, 8, 4]), at=np.array([0, 0, 0]), up=np.array([0, 1, 0])
        )

        self.manipulation_mode = "camera"  # or "object"
        self.rendering_mode = "phong"  # flat, gouraud, wireframe, texture

        # Setup input handler
        self.input_handler = InputHandler(self)
        self.input_handler.setup_callbacks(self.win)

        glfw.set_error_callback(
            lambda code, desc: print("[GLFW ERROR]", code, desc.decode())
        )

        # initialize GUI
        self.gui = GUI(self.win)

    def run(self):
        """Main render loop for this OpenGL windows"""
        while not glfw.window_should_close(self.win):
            # clear draw buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            err = GL.glGetError()
            if err != GL.GL_NO_ERROR:
                print(f"OpenGL Error: {err}")

            proj = self.camera.projection_matrix(self.size)
            view = self.camera.view_matrix()

            # draw scene objects
            if self.display_grid:
                self.grid.draw(proj, view, identity())
            self.scene.draw_all(proj, view, self.rendering_mode)

            # GUI
            self.gui.begin_frame()
            self.gui.render_menu_bar(self)
            self.gui.render_scene_panel(self.scene)
            self.gui.render_info_panel(self)
            self.gui.end_frame()

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()
