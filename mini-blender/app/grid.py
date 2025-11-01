import numpy as np
import OpenGL.GL as GL
from objects.abstract import Drawable
from lib.buffer import VAO, UManager
from lib.shader import Shader


class Grid(Drawable):
    def __init__(
        self,
        shader_type="gouraud",
        size=1000,
        step=1,
        major_every=5,
    ):
        super().__init__(shader_type)

        self.size = size
        self.step = step
        self.major_every = major_every
        self.vertices, self.colors = self._generate_grid_vertices()

        self.vao = VAO()
        self.shader = Shader(shader_type)
        self.uma = UManager(self.shader)

    def setup(self):
        # fmt: off
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None,)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None,)
        self.vao.add_vbo(2, self.normals, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None,)
        if self.indices is not None:
            self.vao.add_ebo(self.indices)

        # Light
        I_light = np.array(
            [
                [0.9, 0.4, 0.6],  # diffuse
                [0.9, 0.4, 0.6],  # specular
                [0.9, 0.4, 0.6],  # ambient
            ],
            dtype=np.float32,
        )
        light_pos = np.array([0, 0.5, 0.9], dtype=np.float32)

        shininess = 100.0
        mode = 1

        # Materials
        K_materials = np.array(
            [
                [0.6, 0.4, 0.7],  # diffuse
                [0.6, 0.4, 0.7],  # specular
                [0.6, 0.4, 0.7],  # ambient
            ],
            dtype=np.float32,
        )

        GL.glUseProgram(self.shader.render_idx)
        self.uma.upload_uniform_matrix3fv(I_light, "I_light", False)
        self.uma.upload_uniform_vector3fv(light_pos, "light_pos")
        self.uma.upload_uniform_matrix3fv(K_materials, "K_materials", False)
        self.uma.upload_uniform_scalar1f(shininess, "shininess")
        self.uma.upload_uniform_scalar1i(mode, "mode")
        return self

    def draw(self, projection, view, model):
        GL.glUseProgram(self.shader.render_idx)

        modelview = view @ model
        self.uma.upload_uniform_matrix4fv(projection, "projection", True)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)

        self.vao.activate()
        GL.glDrawArrays(GL.GL_LINES, 0, len(self.vertices))
        self.vao.deactivate()

    def _generate_grid_vertices(self):
        vertices = []
        colors = []

        # Color scheme: minor lines (gray), major lines (darker gray), axes (red/blue)
        minor_color = [0.3, 0.3, 0.3]
        major_color = [0.5, 0.5, 0.5]
        x_axis_color = [1.0, 0.2, 0.2]  # Red for X
        z_axis_color = [0.2, 0.2, 1.0]  # Blue for Z

        half_size = self.size / 2

        # Generate grid lines parallel to X-axis (running along X, at various Z positions)
        z = -half_size
        while z <= half_size:
            is_major = abs(z) % (self.step * self.major_every) < 0.001
            is_z_axis = abs(z) < 0.001

            # Line from (-half_size, 0, z) to (half_size, 0, z)
            vertices.extend([[-half_size, 0, z], [half_size, 0, z]])

            if is_z_axis:
                colors.extend([x_axis_color, x_axis_color])
            elif is_major:
                colors.extend([major_color, major_color])
            else:
                colors.extend([minor_color, minor_color])

            z += self.step

        # Generate grid lines parallel to Z-axis (running along Z, at various X positions)
        x = -half_size
        while x <= half_size:
            is_major = abs(x) % (self.step * self.major_every) < 0.001
            is_x_axis = abs(x) < 0.001

            # Line from (x, 0, -half_size) to (x, 0, half_size)
            vertices.extend([[x, 0, -half_size], [x, 0, half_size]])

            if is_x_axis:
                colors.extend([z_axis_color, z_axis_color])
            elif is_major:
                colors.extend([major_color, major_color])
            else:
                colors.extend([minor_color, minor_color])

            x += self.step

        return np.array(vertices, dtype=np.float32), np.array(colors, dtype=np.float32)
