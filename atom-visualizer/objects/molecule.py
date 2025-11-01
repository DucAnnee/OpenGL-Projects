from objects import Sphere, Drawable
from objects.bond import Bond
from objects.colors import Color
from lib.transform import translate, rotate, scale

import numpy as np
import OpenGL.GL as GL

ATOM_COLOR = {
    "H": Color.WHITE,
    "C": Color.BLACK,
    "O": Color.RED,
    "N": Color.CYAN,
    "S": Color.YELLOW,
    "P": Color.ORANGE,
    "Cl": Color.GREEN,
    "F": Color.MAGENTA,
}

BOND_GEOMETRIES = {
    # 2 bonds
    "linear": [np.array([1, 0, 0]), np.array([-1, 0, 0])],
    "bent": [  # 104.5 degrees
        np.array([np.cos(np.deg2rad(-37.5)), np.sin(np.deg2rad(-37.5)), 0]),
        np.array([np.cos(np.deg2rad(217.5)), np.sin(np.deg2rad(217.5)), 0]),
    ],
    # 3 bonds
    "trigonal_planar": [
        np.array([np.cos(np.deg2rad(90)), np.sin(np.deg2rad(90)), 0]),  # 90° (up)
        np.array(
            [np.cos(np.deg2rad(210)), np.sin(np.deg2rad(210)), 0]
        ),  # 210° (down-left)
        np.array(
            [np.cos(np.deg2rad(330)), np.sin(np.deg2rad(330)), 0]
        ),  # 330° (down-right)
    ],
    # 4 bonds
    "tetrahedral": [
        np.array([1, 1, 1]),
        np.array([1, -1, -1]),
        np.array([-1, 1, -1]),
        np.array([-1, -1, 1]),
    ],
    "seesaw": [
        np.array([0, 1, 0]),
        np.array([0, -1, 0]),
        np.array([1, 0, 0]),
        np.array([-1, 0, 0]),
    ],
}


class Molecule(Drawable):
    def __init__(self, atom: Sphere, bonding_type, parent_bond_vector=None, name=None):
        self.atom = atom
        self.bonding_type = bonding_type
        self.parent_bond_vector = parent_bond_vector

        self.name = name if name else None
        self.children: list[Molecule] = []
        self.bonds: list[Bond] = []

        self.available_bonds = [
            v / np.linalg.norm(v) for v in BOND_GEOMETRIES.get(bonding_type, [])
        ]  # get unit vectors of the bond directions

        if bonding_type == "double":
            self.bonding_count = 2

    def attach(self, child, bond_length=1.5, bond_radius=0.1, bond_count=1):
        self.children.append(child)

        bond_vector = self.available_bonds.pop(0)

        child_pos = bond_vector * bond_length
        child.atom.transform = translate(*child_pos) @ child.atom.transform

        bond = Bond(
            radius=bond_radius, height=bond_length, bond_count=bond_count
        ).setup()

        y_axis = np.array([0, 1, 0])
        axis = np.cross(y_axis, bond_vector)
        angle = np.arccos(np.dot(y_axis, bond_vector))
        if np.isclose(angle, np.pi):
            axis = np.array([1, 0, 0])  # any axis perpendicular to y_axis

        bond.transform = rotate(axis=axis, radians=angle) @ bond.transform

        self.bonds.append(bond)
        self.children.append(child)

    def draw(self, projection, view, model):
        self.atom.draw(projection, view, model)
        for bond in self.bonds:
            bond.draw(projection, view, model)
        for child in self.children:
            child.draw(projection, view, model)

    @classmethod
    def build_from_recipe(cls, recipe):
        atom_recipe = recipe["atom"]
        atom = Sphere(
            radius=atom_recipe["radius"],
            color=ATOM_COLOR.get(atom_recipe["symbol"], Color.GRAY),
            name=atom_recipe["symbol"],
        ).setup()
        # print("Building atom:", atom_recipe["symbol"])

        molecule = cls(atom, recipe["bonding_type"], name=atom_recipe["symbol"])
        # print("Bonding type:", recipe["bonding_type"])

        for child_recipe in recipe.get("children", []):
            child_molecule = cls.build_from_recipe(child_recipe)
            molecule.attach(
                child_molecule,
                bond_length=child_recipe.get("bond_length", 1.5),
                bond_radius=child_recipe.get("bond_radius", 0.1),
                bond_count=child_recipe.get("bond_count", 1),
            )
            # print("Attached child:", child_recipe["atom"]["symbol"])

        return molecule
