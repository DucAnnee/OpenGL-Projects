import numpy as np
from objects.colors import Color
from objects.abstract import Drawable


class Tetrahedron(Drawable):
    def __init__(self, shader_type="phong"):
        # fmt: off
        super().__init__(shader_type)
        self.vertices = np.array([[+1, +1, +1], # A
                                  [-1, +1, -1], # B
                                  [+1, -1, -1], # C 
                                  [-1, -1, +1]], dtype=np.float32,) # D

        self.indices = np.array([[2, 1, 0], 
                                 [2, 3, 1], 
                                 [0, 1, 3], 
                                 [0, 3, 2]], dtype=np.uint32,).reshape(-1) # flatten to 1D array

        self.normals = np.array([[+1, +1, +1], # A
                                 [-1, +1, -1], # B
                                 [+1, -1, -1], # C 
                                 [-1, -1, +1]], dtype=np.float32,) # D

        self.normals = self.normals / np.linalg.norm(self.normals, axis=1, keepdims=True)
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]

    def draw(self, projection, view, model):
        super().draw(
            projection,
            view,
            model,
        )
