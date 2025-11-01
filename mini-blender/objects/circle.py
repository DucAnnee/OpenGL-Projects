import numpy as np
import OpenGL.GL as GL
from objects.colors import Color
from objects.abstract import Drawable


class Circle(Drawable):
    def __init__(self, shader_type="phong", nsegments=32):
        # fmt: off
        super().__init__(shader_type)
        self.culling = False

        self.nsegments = nsegments

        angles = np.linspace(0, 2 * np.pi, nsegments+1, endpoint=True) + np.pi / 2
        ring = [[np.cos(a), np.sin(a), 0] for a in angles]
        vertices = [[0, 0, 0]] + ring + [[np.cos(0), np.sin(0), 0]]

        self.vertices = np.array(vertices, dtype=np.float32)
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]
        self.normals = np.tile([0, 0, 1], (self.vertices.shape[0], 1)).astype(np.float32)
        self.normals = self.normals / np.linalg.norm(self.normals, axis=1, keepdims=True)

    def draw(self, projection, view, model):
        super().draw(
            projection, view, model, False, GL.GL_TRIANGLE_FAN, 0, self.nsegments + 2
        )
