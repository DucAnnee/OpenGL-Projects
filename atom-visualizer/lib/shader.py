import OpenGL.GL as GL  # standard Python OpenGL wrapper
import numpy as np
import pandas as pd
import sys
import os

from .config import PROJECT_ROOT


class Shader:
    """Helper class to create and automatically destroy shader program"""

    def __init__(self, shader_type: str):
        # fmt: off
        """Shader can be initialized with raw strings or source file names"""
        if shader_type.lower() == "phong":
            vertex_source = os.path.join(PROJECT_ROOT, "shaders", "phong.vert")
            fragment_source = os.path.join(PROJECT_ROOT, "shaders", "phong.frag")
        elif shader_type.lower() == "gouraud":
            vertex_source = os.path.join(PROJECT_ROOT, "shaders", "gouraud.vert")
            fragment_source = os.path.join(PROJECT_ROOT, "shaders", "gouraud.frag")
        else:
            raise ValueError(f"Unknown shader type: {shader_type}")

        self.render_idx = None
        vert = self._compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
        frag = self._compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)
        if vert and frag:
            self.render_idx = GL.glCreateProgram()  # pylint: disable=E1111
            GL.glAttachShader(self.render_idx, vert)
            GL.glAttachShader(self.render_idx, frag)
            GL.glLinkProgram(self.render_idx)
            GL.glDeleteShader(vert)
            GL.glDeleteShader(frag)
            status = GL.glGetProgramiv(self.render_idx, GL.GL_LINK_STATUS)
            if not status:
                print(GL.glGetProgramInfoLog(self.render_idx).decode("ascii"))
                sys.exit(1)

    def __del__(self):
        GL.glUseProgram(0)
        if self.render_idx:  # if this is a valid shader object
            GL.glDeleteProgram(self.render_idx)  # object dies => destroy GL object

    @staticmethod
    def _compile_shader(src, shader_type):
        shader_path = os.path.join(PROJECT_ROOT, src)
        # print(
        #     "[INFO::lib.shader.Shader._compile_shader] reading shader from", shader_path
        # )
        if os.path.exists(shader_path):
            src = open(shader_path, "r").read()
        else:
            print(
                "[ERROR::lib.shader.Shader._compile_shader] Shader source not found, using string as source"
            )
        src = src.decode("ascii") if isinstance(src, bytes) else src
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, src)
        GL.glCompileShader(shader)
        status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        src = ("%3d: %s" % (i + 1, l) for i, l in enumerate(src.splitlines()))
        if not status:
            log = GL.glGetShaderInfoLog(shader).decode("ascii")
            GL.glDeleteShader(shader)
            src = "\n".join(src)
            print("Compile failed for %s\n%s\n%s" % (shader_type, log, src))
            sys.exit(1)
        return shader

    def destroy(self):
        try:
            if getattr(self, "render_idx", None):
                GL.glUseProgram(0)
                GL.glDeleteProgram(self.render_idx)
                self.render_idx = None
        except Exception:
            pass
