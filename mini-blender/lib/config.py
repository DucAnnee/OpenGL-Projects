import os
import numpy as np

# fmt: off
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

GLOBAL_LIGHT_POS = np.array([30.0, 90.0, 30.0], dtype=np.float32)
GLOBAL_I_LIGHT = np.array([[0.9, 0.9, 0.9],   # diffuse 
                           [0.9, 0.9, 0.9],   # specular 
                           [0.05, 0.05, 0.05]],  # ambient 
                           dtype=np.float32,
)
GLOBAL_SHININESS = 20.0
GLOBAL_K_MATERIALS = np.array([[0.9, 0.9, 0.9],   # diffuse 
                               [0.8, 0.8, 0.8],   # specular 
                               [0.1, 0.1, 0.1]],  # ambient 
                               dtype=np.float32)
