from objects import *

OBJECT_FACTORY = {
    "Triangle": lambda: Triangle().setup(),
    "Rectangle": lambda: Rectangle().setup(),
    "Pentagon": lambda: Pentagon().setup(),
    "Hexagon": lambda: Hexagon().setup(),
    "Circle": lambda: Circle().setup(),
    "Ellipse": lambda: Ellipse().setup(),
    "Trapezoid": lambda: Trapezoid().setup(),
    "Star": lambda: Star().setup(),
    "Arrow": lambda: Arrow().setup(),
    "Cube": lambda: Cube().setup(),
    "Sphere": lambda: Sphere().setup(),
    "Cylinder": lambda: Cylinder().setup(),
    "Cone": lambda: Cone().setup(),
    "Tetrahedron": lambda: Tetrahedron().setup(),
    "Torus": lambda: Torus().setup(),
    "Prism": lambda: Cylinder(nsegments=3).setup(),
}

OBJECT_CATEGORIES = {
    "2D": [
        "Triangle",
        "Rectangle",
        "Pentagon",
        "Hexagon",
        "Circle",
        "Ellipse",
        "Trapezoid",
        "Star",
        "Arrow",
    ],
    "3D": [
        "Cube",
        "Sphere",
        "Cylinder",
        "Cone",
        "Tetrahedron",
        "Torus",
        "Prism",
    ],
}
