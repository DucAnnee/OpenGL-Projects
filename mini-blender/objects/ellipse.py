import numpy as np
import OpenGL.GL as GL
from objects.colors import Color
from objects.abstract import Drawable


class Ellipse(Drawable):
    def __init__(
        self, shader_type="phong", major_length=1.0, minor_length=0.5, nsegments=32
    ):
        # fmt: off
        """
        - major_length: length of the major axis
        - minor_length: length of the minor axis
        - nsegments: number of segments to approximate the ellipse
        """
        super().__init__(shader_type)
        self.major_length = major_length
        self.minor_length = minor_length
        self.nsegments = nsegments
        self.culling = False

        self.vertices = self._generate_vertices().astype(np.float32)
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]
        self.normals = np.array([[0, 0, 1]], dtype=np.float32)
        self.normals = self.normals / np.linalg.norm(self.normals, axis=1, keepdims=True)

    def draw(self, projection, view, model):
        super().draw(
            projection, view, model, False, GL.GL_TRIANGLE_FAN, 0, self.nsegments + 1
        )

    def _generate_vertices(self):
        theta = np.linspace(0, 2 * np.pi, self.nsegments, endpoint=False)
        x = self.major_length * np.cos(theta)
        y = self.minor_length * np.sin(theta)
        z = np.zeros_like(x)
        return np.vstack((x, y, z)).T
