import numpy as np
from objects.colors import Color
from objects.abstract import Drawable


class Torus(Drawable):
    def __init__(
        self,
        shader_type="phong",
        major_radius=1,
        minor_radius=0.5,
        major_nsegments=32,
        minor_nsegments=32,
    ):
        # fmt: off
        """
        - major_radius: the distance from the center of the tube to the center of the torus
        - minor_radius: the radius of the tube
        - major_nsegments: number of segments around the major radius
        - minor_nsegments: number of segments around the minor radius
        """
        super().__init__(shader_type)

        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.major_nsegments = major_nsegments
        self.minor_nsegments = minor_nsegments

        self.vertices = self._generate_vertices()
        self.vertices_map = np.arange(self.minor_nsegments*self.major_nsegments).reshape(self.major_nsegments, self.minor_nsegments)
        self.indices = self._generate_indices()
        self.normals = self._generate_normals()
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]
        # self.colors = np.tile([Color.CYAN], (self.vertices.shape[0], 1)).astype(np.float32)

    def _generate_vertices(self):
        """
        x = (R + r·cos(φ))·cos(θ)
        y = (R + r·cos(φ))·sin(θ)
        z = r·sin(φ)
        """
        phi = np.linspace(0, 2 * np.pi, self.minor_nsegments, endpoint=False)
        theta = np.linspace(0, 2 * np.pi, self.major_nsegments, endpoint=False)

        phi_grid, theta_grid = np.meshgrid(
            phi, theta, indexing="ij"
        )  # (minor_nsegments, major_nsegments)

        x = (self.major_radius + self.minor_radius * np.cos(phi_grid)) * np.cos(
            theta_grid
        )
        z = (self.major_radius + self.minor_radius * np.cos(phi_grid)) * np.sin(
            theta_grid
        )
        y = self.minor_radius * np.sin(phi_grid)

        return np.column_stack((x.flatten(), y.flatten(), z.flatten())).astype(
            np.float32
        )

    def _generate_indices(self):
        indices = []

        for i in range(self.major_nsegments):  # i: ring index
            for j in range(self.minor_nsegments):  # : vertex index in ring i
                curr1 = self.vertices_map[i, j]
                curr2 = self.vertices_map[(i + 1) % self.major_nsegments, j]
                next1 = self.vertices_map[i, (j + 1) % self.minor_nsegments]
                next2 = self.vertices_map[
                    (i + 1) % self.major_nsegments, (j + 1) % self.minor_nsegments
                ]

                indices.extend([curr1, curr2, next2])
                indices.extend([next1, curr1, next2])

        return np.array(indices, dtype=np.uint32)

    def _generate_normals(self):
        phi = np.linspace(0, 2 * np.pi, self.minor_nsegments, endpoint=False)
        theta = np.linspace(0, 2 * np.pi, self.major_nsegments, endpoint=False)

        phi_grid, theta_grid = np.meshgrid(phi, theta, indexing="ij")

        nx = (np.cos(phi_grid) * np.cos(theta_grid)).flatten()
        ny = (np.cos(phi_grid) * np.sin(theta_grid)).flatten()
        nz = (np.sin(phi_grid)).flatten()

        return np.vstack((nx, ny, nz), dtype=np.float32).T
