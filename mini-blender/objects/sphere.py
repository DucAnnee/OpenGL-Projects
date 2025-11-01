import numpy as np
from objects.colors import Color
from objects.abstract import Drawable


class Sphere(Drawable):
    def __init__(self, shader_type="phong", radius=1, nsegments=32):
        # fmt: off
        """
        - radius: radius of the sphere
        - nsegments: segments of the ring of the sphere
        """
        super().__init__(shader_type)

        self.radius = radius
        self.nsegments = nsegments

        self.vertices = self._generate_vertices()
        self.vertices_map = np.arange(2, nsegments*(int(nsegments/2)-1)+2).reshape(nsegments, int(nsegments/2)-1)
        self.indices = self._generate_indices()
        self.normals = self._generate_normals()
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]

    def _generate_vertices(self):
        # fmt: off
        """
        x = (r·cos(φ))·cos(θ)
        z = (r·cos(φ))·sin(θ)
        y = r·sin(φ)
        """
        vertices = []

        phi = np.linspace(0, np.pi, int(self.nsegments/2), endpoint=False)[1:] # exclude the north pole
        theta = np.linspace(0, 2*np.pi, self.nsegments, endpoint=False)

        for i in range(len(theta)):
            for j in range(len(phi)):
                vertices.append([self.radius * np.sin(phi[j]) * np.cos(theta[i]),
                                 self.radius * np.cos(phi[j]),
                                 self.radius * np.sin(phi[j]) * np.sin(theta[i])])

        north_pole = np.array([[0, self.radius, 0]], dtype=np.float32)
        south_pole = np.array([[0, -self.radius, 0]], dtype=np.float32)
            
        return np.vstack((north_pole, south_pole, vertices), dtype = np.float32)

    def _generate_indices(self):
        # fmt: off
        indices = []

        # middle quads
        for i in range(self.nsegments):
            for j in range(0, int(self.nsegments/2)-2):
                curr1 = self.vertices_map[i, j]
                curr2 = self.vertices_map[(i+1) % self.nsegments, j]
                next1 = self.vertices_map[i, j+1]
                next2 = self.vertices_map[(i+1) % self.nsegments, j+1]

                indices.extend([curr1, curr2, next2])
                indices.extend([next1, curr1, next2])

        # top and bottom cap
        for i in range(self.nsegments):
            indices.extend([0,self.vertices_map[(i+1) % self.nsegments, 0] , self.vertices_map[i, 0]])
            indices.extend([1, self.vertices_map[i, -1], self.vertices_map[(i+1) % self.nsegments, -1]])

        return np.array(indices, dtype=np.uint32)

    def _generate_normals(self):
        v = self.vertices.astype(np.float32, copy=False)
        n = np.linalg.norm(v, axis=1, keepdims=True)
        n = np.maximum(n, 1e-12)
        return (v / n).astype(np.float32, copy=False)
