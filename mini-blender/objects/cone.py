import numpy as np
from objects.colors import Color
from objects.abstract import Drawable


class Cone(Drawable):
    # fmt: off
    def __init__(self, shader_type="phong", radius=1, height=1, nsegments=32):
        """
        - radius: radius of the base
        - height: height of the cone
        - nsegments: number of segments to approximate the base circle
        """
        super().__init__(shader_type)

        self.radius = radius
        self.height = height
        self.nsegments = nsegments

        self.vertices = self._generate_vertices()
        self.indices = self._generate_indexes()
        self.normals = self._generate_normals()
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]

    def _generate_vertices(self):
        vertices = [[0.0, 0.0, 0.0], [0.0, self.height, 0.0]]  # base center and apex
        for i in range(self.nsegments + 1):
            theta = 2.0 * np.pi * i / self.nsegments
            x = self.radius * np.cos(theta)
            z = self.radius * np.sin(theta)
            y = 0.0
            vertices.append([x, y, z])

        return np.array(vertices, dtype=np.float32)

    def _generate_indexes(self):
        indices = []
        # base
        for i in range(self.nsegments):
            indices.extend([0, i + 2, i + 3])
        # side
        for i in range(self.nsegments):
            indices.extend([1, i + 3, i + 2])
        return np.array(indices, dtype=np.uint32)

    def _generate_normals(self):
        normals = np.zeros(self.vertices.shape, dtype=np.float32)
        # base and apex normal
        normals[0] = [0.0, -1.0, 0.0]
        normals[1] = [0.0, 1.0, 0.0]
        # side normals
        apex = self.vertices[1]
        for i in range(2, self.nsegments + 3):
            p1 = self.vertices[i]
            p2 = self.vertices[i - 1]
            v1 = p1 - apex
            v2 = p2 - apex
            normal = np.cross(v1, v2)
            normal /= np.linalg.norm(normal) + 1e-8
            normals[i] = normal

        normals[2] += normals[self.nsegments + 2]
        normals[self.nsegments + 2] = normals[2]
        # average normals for base vertices
        for i in range(2, self.nsegments + 3):
            # normals[i] += normals[0]
            normals[i] /= np.linalg.norm(normals[i]) + 1e-8
        return normals
