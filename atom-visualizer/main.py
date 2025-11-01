import os

# os.environ["GDK_BACKEND"] = "x11"
import glfw
from app.viewer import Viewer
from objects.atom import Atom
from objects.colors import Color
from objects import Circle


def main():
    """create windows, add shaders & scene objects, then run rendering loop"""
    viewer = Viewer()
    viewer.run()


if __name__ == "__main__":
    glfw.init()
    main()
    glfw.terminate()
