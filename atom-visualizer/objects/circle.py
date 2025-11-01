import numpy as np
import OpenGL.GL as GL
from objects.colors import Color
from objects.abstract import Drawable


class Circle(Drawable):
    def __init__(self, shader_type="gouraud", radius=1.0, nsegments=32):
        # fmt: off
        super().__init__(shader_type)

        self.nsegments = nsegments

        angles = np.linspace(0, 2 * np.pi, nsegments, endpoint=True) 
        vertices = [[radius*np.cos(a), radius*np.sin(a), 0] for a in angles]
        # vertices = [[0, 0, 0]] + ring + [[np.cos(0), np.sin(0), 0]]

        self.vertices = np.array(vertices, dtype=np.float32)
        self.colors = np.tile([Color.WHITE], (self.vertices.shape[0], 1)).astype(np.float32)
        self.normals = np.tile([0, 0, 1], (self.vertices.shape[0], 1)).astype(np.float32)
        self.normals = self.normals / np.linalg.norm(self.normals, axis=1, keepdims=True)

    def draw(self, projection, view, model):
        super().draw(projection, view, model, False, GL.GL_LINE_LOOP, 0, self.nsegments)
