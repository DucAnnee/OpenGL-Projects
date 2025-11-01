import numpy as np
from objects.colors import Color
from objects.abstract import Drawable


class Cylinder(Drawable):
    def __init__(self, shader_type="phong", radius=1, height=1, nsegments=32):
        # fmt: off
        """
        - radius: radius of the base
        - height: height of the cylinder
        - nsegments: number of segments to approximate the base circle
        """
        super().__init__(shader_type)
        self.radius = radius
        self.height = height
        self.nsegments = nsegments

        self.vertices = self._generate_vertices()
        self.indices = self._generate_indexes()
        self.normals = self._generate_normals()
        # self.colors = np.tile([Color.BLUE], (self.vertices.shape[0], 1)).astype(np.float32)
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]

    def _generate_vertices(self):
        # fmt: off
        vertices = [[0.0, 0.0, 0.0], [0.0, self.height, 0.0]]  # bottom base and top base center 
        # bottom
        for i in range(self.nsegments):
            theta = 2.0 * np.pi * i / self.nsegments
            x = self.radius * np.cos(theta)
            z = self.radius * np.sin(theta)
            y = 0.0
            vertices.append([x, y, z])
        # top
        for i in range(self.nsegments):
            theta = 2.0 * np.pi * i / self.nsegments
            x = self.radius * np.cos(theta)
            z = self.radius * np.sin(theta)
            y = self.height
            vertices.append([x, y, z])

        return np.array(vertices, dtype=np.float32)

    def _generate_indexes(self):
        indices = []
        # bottom base
        for i in range(self.nsegments):
            indices.extend([0, i + 2, (i + 1) % self.nsegments + 2])
        # top base
        for i in range(self.nsegments):
            indices.extend(
                [
                    1,
                    (i + 1) % self.nsegments + self.nsegments + 2,
                    i + self.nsegments + 2,
                ]
            )
        # side
        for i in range(self.nsegments):
            bottom1 = i + 2
            bottom2 = (i + 1) % self.nsegments + 2
            top1 = i + self.nsegments + 2
            top2 = (i + 1) % self.nsegments + self.nsegments + 2
            indices.extend([bottom1, top1, bottom2])
            indices.extend([bottom2, top1, top2])

        return np.array(indices, dtype=np.uint32)

    def _generate_normals(self):
        normals = np.zeros(self.vertices.shape, dtype=np.float32)

        # bottom and top center normal
        normals[0] = [0.0, -1.0, 0.0]
        normals[1] = [0.0, 1.0, 0.0]

        # top normals
        for i in range(self.nsegments):
            theta = 2.0 * np.pi * i / self.nsegments
            x = np.cos(theta)
            z = np.sin(theta)
            normals[i + 2] = [x, 0.0, z]
            normals[i + self.nsegments + 2] = [x, 0.0, z]

        # normalize side normals
        for i in range(2, self.vertices.shape[0]):
            normals[i] = normals[i] / np.linalg.norm(normals[i])

        return normals
