import os

# os.environ["GDK_BACKEND"] = "x11"
import glfw
from app.viewer import Viewer
from objects import *


def main():
    """create windows, add shaders & scene objects, then run rendering loop"""
    viewer = Viewer()
    scene = viewer.scene
    scene.add(Torus().setup())
    viewer.run()


if __name__ == "__main__":
    glfw.init()
    main()
    glfw.terminate()
