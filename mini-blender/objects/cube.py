import numpy as np
from objects.colors import Color
from objects.abstract import Drawable


class Cube(Drawable):
    # fmt: off
    def __init__(self, shader_type="phong"):
        super().__init__(shader_type)

        self.vertices = np.array([[+1, -1, +1], # A
                                  [+1, +1, +1], # B
                                  [-1, -1, +1], # C
                                  [-1, +1, +1], # D
                                  [-1, -1, -1], # E
                                  [-1, +1, -1], # F
                                  [+1, -1, -1], # G 
                                  [+1, +1, -1]], dtype=np.float32) # H
        self.indices = np.array([[0, 1, 2], [2, 1, 3],
                                 [2, 3, 4], [4, 3, 5],
                                 [4, 5, 6], [6, 5, 7],
                                 [7, 1, 6], [6, 1, 0],
                                 [7, 5, 1], [1, 5, 3], # top
                                 [2, 4, 0], [0, 4, 6]], dtype=np.uint32,).reshape(-1) # bottom
        # self.colors = np.tile([Color.WHITE], (self.vertices.shape[0], 1)).astype(
        #     np.float32
        # )
        self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        for i in range(self.vertices.shape[0]):
            self.colors[i] = Color.all_colors[i % len(Color.all_colors)]


        self.normals = np.array([[+1, -1, +1], # A
                                 [+1, +1, +1], # B
                                 [-1, -1, +1], # C
                                 [-1, +1, +1], # D
                                 [-1, -1, -1], # E
                                 [-1, +1, -1], # F
                                 [+1, -1, -1], # G 
                                 [+1, +1, -1]], dtype=np.float32) # H
        self.normals = self.normals / np.linalg.norm(self.normals, axis=1, keepdims=True)
