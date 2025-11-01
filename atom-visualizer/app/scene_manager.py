import OpenGL.GL as GL
import numpy as np
from lib.transform import Trackball, translate, rotate, scale, identity
from objects.abstract import Drawable
from objects.atom import Atom
from objects.colors import Color
from objects.molecule import Molecule
from lib.molecule_recipes import recipes


class SceneManager:
    """Manages all objects in the scene"""

    def __init__(self):
        self.current_atom = Atom("phong", Color.RED, 1, "H").setup()
        self.current_molecule_name = "H2O"
        self.current_molecule = Molecule.build_from_recipe(
            recipes[self.current_molecule_name]
        )

    def set_current_atom(self, obj):
        self.current_atom = obj

    def get_current_atom(self):
        return self.current_atom

    def get_current_atom_name(self):
        return self.current_atom.name if self.current_atom else "None"

    def set_current_molecule(self, obj):
        self.current_molecule = obj

    def get_current_molecule(self):
        return self.current_molecule

    def get_current_molecule_name(self):
        return self.current_molecule.name if self.current_molecule else "None"

    def set_current_molecule_name(self, name):
        self.current_molecule.name = name

    def draw(self, projection, view, model, rendering_mode):
        if rendering_mode == "atom" and self.current_atom:
            self.current_atom.draw(projection, view, model)
        elif rendering_mode == "molecule":
            self.current_molecule.draw(projection, view, model)
        else:
            pass
