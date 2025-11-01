import numpy as np
from objects.colors import Color
from objects.abstract import Drawable


class Bond(Drawable):
    def __init__(
        self, shader_type="phong", radius=0.1, height=1.0, bond_count=1, nsegments=16
    ):
        # fmt: off
        """
        - radius: radius of each cylinder
        - height: height of the bond
        - bond_count: 1 (single), 2 (double), or 3 (triple)
        - nsegments: number of segments to approximate the cylinder circle
        """
        super().__init__(shader_type)
        self.radius = radius
        self.height = height
        self.nsegments = nsegments
        self.bond_count = bond_count

        # Generate offset positions for multiple bonds
        self.bond_offsets = self._calculate_bond_offsets()
        
        self.vertices = self._generate_vertices()
        self.indices = self._generate_indexes()
        self.normals = self._generate_normals()
        self.colors = np.tile([Color.GRAY], (self.vertices.shape[0], 1)).astype(np.float32)

    def _calculate_bond_offsets(self):
        spacing = self.radius * 2.5  # distance between parallel bonds

        if self.bond_count == 1:
            return [np.array([0.0, 0.0, 0.0])]
        elif self.bond_count == 2:
            return [
                np.array([spacing / 2, 0.0, 0.0]),
                np.array([-spacing / 2, 0.0, 0.0]),
            ]
        elif self.bond_count == 3:
            return [
                np.array([0.0, 0.0, 0.0]),
                np.array([spacing, 0.0, 0.0]),
                np.array([-spacing, 0.0, 0.0]),
            ]
        else:
            return [np.array([0.0, 0.0, 0.0])]

    def _generate_single_cylinder_vertices(self, offset):
        # fmt: off
        vertices = [[offset[0], 0.0, offset[2]],  # bottom center 
                    [offset[0], self.height, offset[2]]]  # top center
            
        # bottom circle
        for i in range(self.nsegments):
            theta = 2.0 * np.pi * i / self.nsegments
            x = offset[0] + self.radius * np.cos(theta)
            z = offset[2] + self.radius * np.sin(theta)
            vertices.append([x, 0.0, z])

        # top circle
        for i in range(self.nsegments):
            theta = 2.0 * np.pi * i / self.nsegments
            x = offset[0] + self.radius * np.cos(theta)
            z = offset[2] + self.radius * np.sin(theta)
            vertices.append([x, self.height, z])
        return vertices

    def _generate_vertices(self):
        all_vertices = []
        for offset in self.bond_offsets:
            cylinder_verts = self._generate_single_cylinder_vertices(offset)
            all_vertices.extend(cylinder_verts)
        return np.array(all_vertices, dtype=np.float32)

    def _generate_indexes(self):
        # fmt: off
        indices = []
        verts_per_cylinder = 2 + 2 * self.nsegments

        for bond_idx in range(self.bond_count):
            base_offset = bond_idx * verts_per_cylinder

            # bottom base (center is at base_offset)
            for i in range(self.nsegments):
                indices.extend([base_offset, 
                                base_offset + i + 2, 
                                base_offset + (i + 1) % self.nsegments + 2])
            # top base (center is at base_offset+1)
            for i in range(self.nsegments):
                indices.extend([base_offset + 1, 
                                base_offset + (i + 1) % self.nsegments + self.nsegments + 2, 
                                base_offset + i + self.nsegments + 2])
            # side faces
            for i in range(self.nsegments):
                bottom1 = base_offset + i + 2
                bottom2 = base_offset + (i + 1) % self.nsegments + 2
                top1 = base_offset + i + self.nsegments + 2
                top2 = base_offset + (i + 1) % self.nsegments + self.nsegments + 2
                indices.extend([bottom1, top1, bottom2])
                indices.extend([bottom2, top1, top2])

        return np.array(indices, dtype=np.uint32)

    def _generate_normals(self):
        normals = np.zeros(self.vertices.shape, dtype=np.float32)
        verts_per_cylinder = 2 + 2 * self.nsegments

        for bond_idx in range(self.bond_count):
            base_offset = bond_idx * verts_per_cylinder

            # bottom and top center normals
            normals[base_offset + 0] = [0.0, -1.0, 0.0]
            normals[base_offset + 1] = [0.0, 1.0, 0.0]

            # side normals
            for i in range(self.nsegments):
                theta = 2.0 * np.pi * i / self.nsegments
                x = np.cos(theta)
                z = np.sin(theta)
                normals[base_offset + i + 2] = [x, 0.0, z]
                normals[base_offset + i + self.nsegments + 2] = [x, 0.0, z]

        # normalize
        for i in range(self.vertices.shape[0]):
            norm = np.linalg.norm(normals[i])
            if norm > 0:
                normals[i] = normals[i] / norm

        return normals
