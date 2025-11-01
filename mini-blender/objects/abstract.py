import ctypes
import numpy as np
from lib.buffer import UManager, VAO
from lib.shader import Shader
import OpenGL.GL as GL
from objects.colors import Color
from lib.config import (
    GLOBAL_I_LIGHT,
    GLOBAL_K_MATERIALS,
    GLOBAL_SHININESS,
    GLOBAL_LIGHT_POS,
)


class Drawable:
    def __init__(self, shader_type: str):
        self.vertices: np.ndarray = None
        self.normals: np.ndarray = None
        self.indices: np.ndarray = None
        self.colors = np.ndarray = None

        self.rendering_mode = "phong"
        self.culling = True

        self.vao: VAO = VAO()
        # self.shader: Shader = Shader(shader_type)
        # self.uma: UManager = UManager(self.shader)
        self.shaders = {
            "flat": Shader("flat"),
            "gouraud": Shader("gouraud"),
            "phong": Shader("phong"),
            "texture": Shader("phong_texture"),
        }

        self.uma = {
            "flat": UManager(self.shaders["flat"]),
            "gouraud": UManager(self.shaders["gouraud"]),
            "phong": UManager(self.shaders["phong"]),
            "texture": UManager(self.shaders["texture"]),
        }

    def setup(self):
        # fmt: off
        self.vao.add_vbo(0, self.vertices, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None,)
        self.vao.add_vbo(1, self.colors, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None,)
        self.vao.add_vbo(2, self.normals, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None,)
        if self.indices is not None:
            self.vao.add_ebo(self.indices)

        for shader, uma in zip(self.shaders.values(), self.uma.values()):
            GL.glUseProgram(shader.render_idx)
            uma.upload_uniform_matrix3fv(GLOBAL_I_LIGHT, "I_light", False)
            uma.upload_uniform_vector3fv(GLOBAL_LIGHT_POS, "light_pos")
            uma.upload_uniform_matrix3fv(GLOBAL_K_MATERIALS, "K_materials", False)
            uma.upload_uniform_scalar1f(GLOBAL_SHININESS, "shininess")
            uma.upload_uniform_scalar1i(1, "mode")
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
        modelview = view @ model
        uma = self.uma[self.rendering_mode]

        uma.upload_uniform_matrix4fv(projection, "projection", True)
        uma.upload_uniform_matrix4fv(modelview, "modelview", True)
        light_pos_eye4 = view @ np.array([GLOBAL_LIGHT_POS[0], GLOBAL_LIGHT_POS[1], GLOBAL_LIGHT_POS[2], 1.0], dtype=np.float32)
        uma.upload_uniform_vector3fv(light_pos_eye4[:3], "light_pos")

        self.vao.activate()
        prev_cull = GL.glIsEnabled(GL.GL_CULL_FACE)
        if self.culling:
            GL.glEnable(GL.GL_CULL_FACE)
        else:
            GL.glDisable(GL.GL_CULL_FACE)

        if use_ebo:
            GL.glDrawElements(mode, int(self.indices.size), GL.GL_UNSIGNED_INT, ctypes.c_voidp(0))
        else:
            GL.glDrawArrays(mode, begin, num)

        if prev_cull:
            GL.glEnable(GL.GL_CULL_FACE)
        else:
            GL.glDisable(GL.GL_CULL_FACE)

        self.vao.deactivate()

    def set_rendering_mode(self, rendering_mode):
        if rendering_mode == "wireframe":
            self.rendering_mode = "flat"
            return
        self.rendering_mode = rendering_mode

    def destroy(self):
        self.vao.destroy()
        for shader in self.shaders.values():
            shader.destroy()
