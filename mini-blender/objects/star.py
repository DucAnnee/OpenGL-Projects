import numpy as np
import OpenGL.GL as GL
from objects.colors import Color
from objects.abstract import Drawable


class Star(Drawable):
    def __init__(
        self, shader_type="phong", nstar=5, inner_radius=0.5, outer_radius=1.0
    ):
        # fmt: off
        """
        - nstar: number of star points
        - inner_radius: radius of the inner vertices
        - outer_radius: radius of the outer vertices
        """
        super().__init__(shader_type)
        self.culling = False

        self.nstar = nstar
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

        self.vertices = self._generate_vertices().astype(np.float32)
        self.normals = np.array([[0, 0, 1]], dtype=np.float32)
        self.normals = self.normals / np.linalg.norm(self.normals, axis=1, keepdims=True)
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]

    def draw(self, projection, view, model):
        super().draw(
            projection, view, model, False, GL.GL_TRIANGLE_FAN, 0, self.nstar * 2 + 2
        )

    def _generate_vertices(self):
        # fmt: off
        theta = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, self.nstar * 2, endpoint=False)
        x = []
        y = []
        z = np.zeros_like(theta)
        for i in range(len(theta)):
            radius = self.outer_radius if i % 2 == 0 else self.inner_radius
            x.append(radius * np.cos(theta[i]))
            y.append(radius * np.sin(theta[i]))
        out_vertices = np.vstack([x, y, z]).T
        out_vertices = np.vstack([out_vertices, out_vertices[0]])
        center = np.array([0, 0, 0], dtype=np.float32)

        return np.vstack([center, out_vertices])
