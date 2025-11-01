from objects import Sphere, Drawable, Circle
from objects.colors import Color
from lib.transform import translate

import numpy as np


class Atom(Drawable):
    def __init__(self, shader_type="phong", color=None, num_e=None, name=None):
        assert num_e is not None, "num_e must be specified"
        assert name is not None, "name must be specified"

        self.name = name
        self.color = color if color else Color.RED
        self.num_e = num_e
        self.electron_shell = []
        self.electron_positions = []

        self.bohr_radius = 1
        self.radius_increment = 0.5

        self._time = 0.0
        self._time_increment = 0.02

        self.atom = Sphere(shader_type, color, 0.5, 32).setup()
        self.electron = Sphere("phong", Color.BLUE, 0.1, 32).setup()
        self.distribute_e()

    def setup(self):
        return self

    def draw(self, projection, view, model):
        # fmt: off
        self._time += self._time_increment

        self.atom.draw(projection, view, model)

        for shell_idx, positions in enumerate(self.electron_positions):
            radius = self.bohr_radius + shell_idx * self.radius_increment
            Circle("gouraud", radius, 64).setup().draw(projection, view, model)

            angular_velocity = 1/(shell_idx+1)
            rotation_angle = self._time*angular_velocity
            cos_angle, sin_angle = np.cos(rotation_angle), np.sin(rotation_angle)

            for pos in positions:
                x_rotated = pos[0]*cos_angle - pos[1]*sin_angle
                y_rotated = pos[0]*sin_angle + pos[1]*cos_angle

                e_model = model @ translate(x_rotated, y_rotated, 0)
                self.electron.draw(projection, view, e_model)

    def distribute_e(self):
        from pprint import pprint

        shell_capacity = [2, 8, 18, 32, 50, 72, 98]
        remaining_e = self.num_e

        for capacity in shell_capacity:
            if remaining_e <= 0:
                break
            electrons_in_shell = min(remaining_e, capacity)
            self.electron_shell.append(electrons_in_shell)
            remaining_e -= electrons_in_shell

        # pprint(self.electron_shell)

        for shell_idx, count in enumerate(self.electron_shell):
            theta = np.linspace(0, 2 * np.pi, count, endpoint=False)
            # pprint(theta)
            radius = self.bohr_radius + shell_idx * self.radius_increment
            positions = np.array(
                [[radius * np.cos(t), radius * np.sin(t), 0] for t in theta]
            )
            # pprint(positions)
            self.electron_positions.append(positions)
        # print(self.electron_positions)
