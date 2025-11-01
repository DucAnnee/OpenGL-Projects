import OpenGL.GL as GL
import numpy as np
from lib.transform import Trackball, translate, rotate, scale, identity
from objects.abstract import Drawable


class SceneObject:
    """Wrapper for drawable objects with transformation state because I don't want to modify the original classes"""

    def __init__(self, drawable: Drawable, name: str = "Object"):
        self.drawable = drawable
        self.name = name

        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.scale_factor = np.array([1.0, 1.0, 1.0], dtype=np.float32)

        self.visible = True
        self.selected = False

        self.trackball = Trackball(distance=0)

    def get_model_matrix(self):
        # order: TRS => Scale -> Rotate -> Translate
        model = identity()
        model = scale(*self.scale_factor) @ model
        model = self.trackball.matrix() @ model
        # model = rotate((0, 1, 0), self.rotation[0]) @ model  # yaw (Y)
        # model = rotate((1, 0, 0), self.rotation[1]) @ model  # pitch (X)
        # model = rotate((0, 0, 1), self.rotation[2]) @ model  # roll (Z)
        model = translate(*self.position) @ model
        return model

    def translate(self, dx, dy, dz):
        self.position += np.array([dx, dy, dz], dtype=np.float32)

    def drag(self, old_pos, new_pos, winsize):
        self.trackball.drag(old_pos, new_pos, winsize)

    def reset_transform(self):
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.trackball.rotation = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        self.scale_factor = np.array([1.0, 1.0, 1.0], dtype=np.float32)


class SceneManager:
    """Manages all objects in the scene"""

    def __init__(self):
        self.objects: list[SceneObject] = []
        self.selected_index = None
        self.curr_rendering_mode = "phong"

    def add(self, drawable: Drawable, name: str = ""):
        if name == "":
            name = f"{drawable.__class__.__name__}_{len(self.objects)}"
        scene_obj = SceneObject(drawable, name)
        self.objects.append(scene_obj)
        self.selected_index = len(self.objects) - 1
        return scene_obj

    def remove(self, index: int):
        if 0 <= index < len(self.objects):
            obj = self.objects.pop(index)
            if hasattr(obj.drawable, "destroy"):
                obj.drawable.destroy()
            if self.selected_index == index:
                self.selected_index = None
            elif self.selected_index is not None and self.selected_index > index:
                self.selected_index -= 1

    def clear(self):
        for obj in self.objects:
            if hasattr(obj.drawable, "destroy"):
                obj.drawable.destroy()
        self.objects.clear()
        self.selected_index = None

    def select(self, index: int):
        if self.selected_index is not None:
            self.objects[self.selected_index].selected = False

        if 0 <= index < len(self.objects):
            self.selected_index = index
            self.objects[index].selected = True
        else:
            self.selected_index = None

    def select_next(self):
        if not self.objects:
            return
        if self.selected_index is None:
            self.select(0)
        else:
            self.select((self.selected_index + 1) % len(self.objects))

    def select_previous(self):
        if not self.objects:
            return
        if self.selected_index is None:
            self.select(len(self.objects) - 1)
        else:
            self.select((self.selected_index - 1) % len(self.objects))

    def get_selected(self):
        if self.selected_index is not None:
            return self.objects[self.selected_index]
        return None

    def draw_all(self, projection, view, rendering_mode):
        if rendering_mode != self.curr_rendering_mode:
            for obj in self.objects:
                if hasattr(obj.drawable, "set_rendering_mode"):
                    obj.drawable.set_rendering_mode(rendering_mode)
            self.curr_rendering_mode = rendering_mode

        if rendering_mode == "wireframe":
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        else:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        for obj in self.objects:
            if obj.visible:
                model = obj.get_model_matrix()
                obj.drawable.draw(projection, view, model)

    def manipulate_selected(self, action: str, value=0.1):
        """
        actions:
            'translate_x', 'translate_y', 'translate_z'
            'reset'
        """
        selected = self.get_selected()
        if selected is None:
            return

        if action == "translate_x":
            selected.translate(value, 0, 0)
        elif action == "translate_y":
            selected.translate(0, value, 0)
        elif action == "translate_z":
            selected.translate(0, 0, value)
        elif action == "reset":
            selected.reset_transform()
