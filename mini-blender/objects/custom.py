import os
import numpy as np
import OpenGL.GL as GL
import pyassimp

from lib.shader import Shader
from lib.buffer import UManager, VAO
from lib.config import (
    PROJECT_ROOT,
    GLOBAL_I_LIGHT,
    GLOBAL_K_MATERIALS,
    GLOBAL_SHININESS,
    GLOBAL_LIGHT_POS,
)

from objects.colors import Color
from objects.abstract import Drawable


class CustomModel(Drawable):
    def __init__(self, shader_type="phong_texture", model_path=None):
        if model_path is None:
            raise ValueError("Model path must be provided")
        model_path = (
            os.path.join(PROJECT_ROOT, model_path)
            if not os.path.exists(model_path)
            else model_path
        )

        self.meshes = self.load_model(model_path)
        if not self.meshes:
            raise RuntimeError(f"No meshes found in model: {model_path}")

        self.normalize_model(center=True, scale=True)
        self.load_textures(model_path)

        for mesh in self.meshes:
            mesh["vao"] = VAO()
            mesh["shader"] = Shader(shader_type)
            mesh["uma"] = UManager(mesh["shader"])
            mesh["texture_id"] = None

    def setup(self):
        for mesh in self.meshes:
            self.setup_mesh(mesh)
        return self

    def setup_mesh(self, mesh):
        # fmt: off
        mesh["vao"].add_vbo(0, mesh["vertices"], ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        mesh["vao"].add_vbo(1, mesh["normals"], ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)
        mesh["vao"].add_vbo(3, mesh["colors"], ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        GL.glUseProgram(mesh["shader"].render_idx)

        if "texcoords" in mesh and mesh["texcoords"] is not None:
            mesh["vao"].add_vbo(2, mesh["texcoords"], ncomponents=2, dtype=GL.GL_FLOAT, normalized=False, stride=0, offset=None)

        if mesh["indices"] is not None:
            mesh["vao"].add_ebo(mesh["indices"])

        if (
            "texture_path" in mesh
            and mesh["texture_path"] is not None
            and mesh.get("has_valid_texcoords", False)
        ):
            mesh["uma"].setup_texture("texture", mesh["texture_path"])


        phong_factor = 0.1

        mesh["uma"].upload_uniform_matrix3fv(GLOBAL_I_LIGHT, "I_light", False)
        mesh["uma"].upload_uniform_vector3fv(GLOBAL_LIGHT_POS, "light_pos")
        mesh["uma"].upload_uniform_matrix3fv(GLOBAL_K_MATERIALS, "K_materials", False)
        mesh["uma"].upload_uniform_scalar1f(GLOBAL_SHININESS, "shininess")
        mesh["uma"].upload_uniform_scalar1f(phong_factor, "phong_factor")
        return self

    def draw(self, projection, view, model):
        modelview = view @ model

        for mesh in self.meshes:
            GL.glUseProgram(mesh["shader"].render_idx)

            mesh["uma"].upload_uniform_matrix4fv(projection, "projection", True)
            mesh["uma"].upload_uniform_matrix4fv(modelview, "modelview", True)
            light_pos_eye4 = view @ np.array(
                [GLOBAL_LIGHT_POS[0], GLOBAL_LIGHT_POS[1], GLOBAL_LIGHT_POS[2], 1.0],
                dtype=np.float32,
            )
            mesh["uma"].upload_uniform_vector3fv(light_pos_eye4[:3], "light_pos")

            mesh["vao"].activate()
            if mesh["vao"].ebo is not None:
                GL.glDrawElements(
                    GL.GL_TRIANGLES, int(mesh["indices"].size), GL.GL_UNSIGNED_INT, None
                )
            else:
                GL.glDrawArrays(GL.GL_TRIANGLES, 0, int(mesh["vertices"].shape[0]))
            mesh["vao"].deactivate()

    def destroy(self):
        for mesh in self.meshes:
            mesh["vao"].destroy()
            mesh["shader"].destroy()

    def load_model(self, model_path):
        meshes = []
        with pyassimp.load(model_path) as scene:
            if not scene or not scene.meshes:
                raise RuntimeError(f"Failed to load or no meshes: {model_path}")

            for mesh_idx, mesh in enumerate(scene.meshes):
                vertices = np.asarray(mesh.vertices, dtype=np.float32)

                if hasattr(mesh, "normals") and len(mesh.normals):
                    normals = np.asarray(mesh.normals, dtype=np.float32)
                else:
                    normals = np.zeros_like(vertices, dtype=np.float32)

                indices = []
                if hasattr(mesh, "faces") and len(mesh.faces):
                    for face in mesh.faces:
                        indices.extend(face)
                if indices:
                    indices = np.array(indices, dtype=np.uint32)
                else:
                    indices = None

                texcoords = None
                has_valid_texcoords = False
                if hasattr(mesh, "texturecoords") and mesh.texturecoords is not None:
                    if (
                        len(mesh.texturecoords) > 0
                        and mesh.texturecoords[0] is not None
                    ):
                        texcoords = np.array(
                            mesh.texturecoords[0][:, :2], dtype=np.float32
                        )
                        # Flip V coordinate
                        texcoords[:, 1] = 1.0 - texcoords[:, 1]

                colors = np.tile([Color.WHITE], (vertices.shape[0], 1)).astype(
                    np.float32
                )

                meshes.append(
                    {
                        "vertices": vertices,
                        "normals": normals,
                        "indices": indices,
                        "texcoords": texcoords,
                        "colors": colors,
                        "has_valid_texcoords": has_valid_texcoords,
                    }
                )

        return meshes

    def load_textures(self, model_path):
        directory = os.path.dirname(model_path)

        with pyassimp.load(model_path) as scene:
            for mesh_idx, mesh in enumerate(self.meshes):
                if mesh_idx >= len(scene.meshes):
                    continue

                assimp_mesh = scene.meshes[mesh_idx]

                if (
                    assimp_mesh.materialindex is not None
                    and assimp_mesh.materialindex < len(scene.materials)
                ):
                    material = scene.materials[assimp_mesh.materialindex]
                    prop_keys = list(material.properties.keys())
                    texture_path = None

                    # Try to get texture using internal dictionary
                    try:
                        for key in list(dict.keys(material.properties)):
                            if "file" in str(key).lower():
                                val = dict.__getitem__(material.properties, key)
                                texture_path = val
                                break
                    except Exception:
                        pass

                    # Check if material has textures attribute
                    if not texture_path:
                        try:
                            if hasattr(material, "textures"):
                                for tex_type, tex_path in material.textures.items():
                                    if tex_type == 1:  # Diffuse texture
                                        texture_path = tex_path
                                        break
                        except Exception:
                            pass

                    # Try common semantic indices for 'file' property
                    if not texture_path and "file" in prop_keys:
                        for semantic in range(10):
                            try:
                                val = material.properties.get(("file", semantic))
                                if val:
                                    texture_path = val
                                    break
                            except:
                                pass

                    if texture_path:
                        texture_filename = os.path.basename(texture_path)
                        full_path = os.path.join(directory, texture_filename)

                        if os.path.exists(full_path):
                            mesh["texture_path"] = full_path

    def normalize_model(self, center=True, scale=True):
        all_vertices = []
        for mesh in self.meshes:
            all_vertices.append(mesh["vertices"])
        all_vertices = np.vstack(all_vertices)

        min_coords = all_vertices.min(axis=0)
        max_coords = all_vertices.max(axis=0)
        center_point = (min_coords + max_coords) / 2
        extent = max_coords - min_coords
        max_extent = extent.max()

        for mesh in self.meshes:
            if center:
                mesh["vertices"] -= center_point
                mesh["vertices"] += np.array([0, extent[1] / 2, 0])

            if scale and max_extent > 0:
                mesh["vertices"] /= max_extent / 10
