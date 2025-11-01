import ctypes
import numpy as np
from lib.transform import identity
from lib.buffer import UManager, VAO
from lib.shader import Shader
import OpenGL.GL as GL
from objects.colors import Color


class Drawable:
    def __init__(self, shader_type: str):
        self.name = None

        self.vertices: np.ndarray = None
        self.normals: np.ndarray = None
        self.indices: np.ndarray = None
        self.colors = np.ndarray = None

        self.rendering_mode = "phong"

        self.vao: VAO = VAO()
        self.shader: Shader = Shader(shader_type)
        self.uma: UManager = UManager(self.shader)

        self.transform = identity()

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
                [0.9, 0.9, 0.9],  # diffuse 
                [0.9, 0.9, 0.9],  # specular 
                [0.05, 0.05, 0.05],  # ambient 
            ],
            dtype=np.float32,
        )
        light_pos = np.array([30.0, 30.0, 30.0], dtype=np.float32)

        shininess = 20.0
        mode = 1

        # Materials
        K_materials = np.array(
            [
                [0.9, 0.9, 0.9],  # diffuse
                [0.8, 0.8, 0.8],  # specular
                [0.1, 0.1, 0.1],  # ambient
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

    def draw(
        self,
        projection,
        view,
        model,
        use_ebo=True,
        mode=GL.GL_TRIANGLES,
        begin=0,
        num=0,
    ):
        # fmt: off
        modelview = view @ model @ self.transform

        light_pos = np.array([30.0, 30.0, 30.0], dtype=np.float32)

        self.uma.upload_uniform_matrix4fv(projection, "projection", True)
        self.uma.upload_uniform_matrix4fv(modelview, "modelview", True)
        light_pos_eye4 = view @ np.array([light_pos[0], light_pos[1], light_pos[2], 1.0], dtype=np.float32)
        self.uma.upload_uniform_vector3fv(light_pos_eye4[:3], "light_pos")

        self.vao.activate()
        if use_ebo:
            GL.glDrawElements(mode, int(self.indices.size), GL.GL_UNSIGNED_INT, ctypes.c_voidp(0))
        else:
            GL.glDrawArrays(mode, begin, num)

        self.vao.deactivate()

    def destroy(self):
        self.vao.destroy()
        self.shader.destroy()
