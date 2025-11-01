import ctypes
import sympy as sp
import numpy as np
import OpenGL.GL as GL
from objects.colors import Color
from objects.abstract import Drawable


class Equation(Drawable):
    def __init__(
        self,
        shader_type="phong",
        func=None,
        step=0.5,
        limit_x=(-10, 10),
        limit_y=(-10, 10),
    ):
        # fmt: off
        """
        - func: a function that takes in (x, y) and returns z
        - step: step size for sampling the function
        - limit_x: (min, max) limits for x
        - limit_y: (min, max) limits for y
        """
        super().__init__(shader_type)

        if func is None:
            raise ValueError("Function 'func' must be provided")
        self.func = self.string_to_lambda(func)
        self.step = step
        self.limit_x = limit_x
        self.limit_y = limit_y
        self.culling = False

        self.vertices = self._generate_vertices()
        self.indices = self._generate_indices()
        self.normals = self._generate_normals()
        self.colors = np.tile([Color.CYAN], (self.vertices.shape[0], 1)).astype(np.float32)
        # self.colors = np.zeros((self.vertices.shape[0], 3), dtype=np.float32)
        # for i in range(self.vertices.shape[0]):
        #     self.colors[i] = Color.all_colors[i % len(Color.all_colors)]

    def draw(self, projection, view, model):
        super().draw(projection, view, model, True, GL.GL_TRIANGLE_STRIP)

    def _generate_vertices(self):
        # fmt: off
        vertices = []
        for x in np.arange(self.limit_x[0], self.limit_x[1], self.step):
            for y in np.arange(self.limit_y[0], self.limit_y[1], self.step):
                z = self.func(x, y)
                vertices.append([x, y, z])

        return np.array(vertices, dtype=np.float32)

    def _generate_indices(self):
        # fmt: off
        indices = []

        num_x = int((self.limit_x[1] - self.limit_x[0]) / self.step)
        num_y = int((self.limit_y[1] - self.limit_y[0]) / self.step)
        for i in range(num_y - 1):
            if i % 2 == 0:
                for j in range(num_x):
                    indices.append(j + i * num_x)
                    indices.append(j + (i + 1) * num_x)
            else:
                for j in reversed(range(num_x)):
                    indices.append(j + (i + 1) * num_x)
                    indices.append(j + i * num_x)

        return np.array(indices, dtype=np.uint32)

    def _generate_normals(self):
        v = self.vertices.astype(np.float32, copy=False)
        n = np.linalg.norm(v, axis=1, keepdims=True)
        n = np.maximum(n, 1e-12)
        return (v / n).astype(np.float32, copy=False)

    @staticmethod
    def string_to_lambda(equation_str, variables=["x", "y"]):
        symbols = sp.symbols(" ".join(variables))

        try:
            expr = sp.sympify(equation_str)
        except (sp.SympifyError, SyntaxError) as e:
            raise ValueError(f"Invalid equation: {equation_str}. Error: {e}")

        func = sp.lambdify(symbols, expr, modules=["numpy"])

        def wrapper(*args):
            result = func(*args)
            if isinstance(result, (int, float, np.number)):
                return float(result)
            return result

        return wrapper
