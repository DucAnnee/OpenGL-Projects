import numpy as np
import OpenGL.GL as GL
from objects.colors import Color
from objects.abstract import Drawable


class Trapezoid(Drawable):
    def __init__(self, shader_type="phong", base_length=4.0, top_length=3, height=2.0):
        # fmt: off
        """
        - base_length: length of the bottom base
        - top_length: length of the top base
        - height: height of the trapezoid
        """
        super().__init__(shader_type)
        self.culling = False

        self.vertices = np.array([[-base_length/2, -height/2, +0], 
                                  [+base_length/2, -height/2, +0], 
                                  [+top_length/2, +height/2, +0], 
                                  [-top_length/2, +height/2, +0]], dtype=np.float32)

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
