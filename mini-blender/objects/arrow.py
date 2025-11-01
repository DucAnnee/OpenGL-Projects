import numpy as np
import OpenGL.GL as GL
from objects.colors import Color
from objects.abstract import Drawable


class Arrow(Drawable):
    def __init__(
        self,
        shader_type="phong",
        stem_length=1.5,
        stem_width=1,
        head_length=1,
        head_width=1.5,
    ):
        # fmt: off
        """
        - stem_length: Length of the arrow's stem.
        - stem_width: Width of the arrow's stem.
        - head_length: Length of the arrow's head.
        - head_width: Width of the arrow's head.
        """
        super().__init__(shader_type)

        self.stem_length = stem_length
        self.stem_width = stem_width
        self.head_length = head_length
        self.head_width = head_width
        
        self.culling = False

        self.vertices = self._generate_vertices().astype(np.float32)
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]
        self.normals = np.tile([0, 0, 1], (self.vertices.shape[0], 1)).astype(np.float32)
        self.normals = self.normals / np.linalg.norm(self.normals, axis=1, keepdims=True)

    def draw(self, projection, view, model):
        super().draw(
            projection,
            view,
            model,
            False,
            GL.GL_TRIANGLE_STRIP,
            0,
            self.vertices.shape[0],
        )

    def _generate_vertices(self):
        # fmt: off
        half_length = (self.stem_length + self.head_length) / 2
        half_stem_width = self.stem_width / 2
        half_head_width = self.head_width / 2
        bottom = -half_length
        head_bottom = bottom + self.stem_length
        head_top = half_length

        stem = np.array([[+bottom, +half_stem_width, 0],
                         [+bottom, -half_stem_width, 0],
                         [head_bottom, +half_stem_width, 0],
                         [head_bottom, -half_stem_width, 0]], dtype=np.float32)

        head = np.array([[head_bottom, +half_head_width, 0],
                         [head_bottom, -half_head_width, 0],
                         [head_top, 0, 0]], dtype=np.float32)

        return np.vstack((stem, head))
