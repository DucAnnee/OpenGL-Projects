import numpy as np
import OpenGL.GL as GL
from objects.colors import Color
from objects.abstract import Drawable


class Rectangle(Drawable):
    def __init__(self, shader_type="phong"):
        # fmt: off
        super().__init__(shader_type)
        self.culling = False

        self.vertices = np.array([[-1, -1, +0], 
                                  [+1, -1, +0], 
                                  [+1, +1, +0], 
                                  [-1, +1, +0]], dtype=np.float32)

        self.normals = np.array([[0, 0, 1],
                                 [0, 0, 1],
                                 [0, 0, 1],
                                 [0, 0, 1]], dtype=np.float32)
        self.normals = self.normals / np.linalg.norm(self.normals, axis=1, keepdims=True)
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]

    def draw(self, projection, view, model):
        super().draw(projection, view, model, False, GL.GL_TRIANGLE_FAN, 0, 4)
