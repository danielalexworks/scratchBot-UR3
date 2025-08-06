import numpy as np

rotation_matrix = np.array([
    [-0.81301595,  0.58197951,  0.01746159],
    [ 0.58197951,  0.81318413, -0.00560518],
    [-0.01746159,  0.00560518, -0.99983182]
])

determinant = np.linalg.det(rotation_matrix)
print("Determinant:", determinant)