import numpy as np
import canvas
import time
from math import radians, sin, cos

# Define cube vertices
def get_cube_vertices(size=1):
    d = size / 2
    return np.array([
        [-d, -d, -d],
        [ d, -d, -d],
        [ d,  d, -d],
        [-d,  d, -d],
        [-d, -d,  d],
        [ d, -d,  d],
        [ d,  d,  d],
        [-d,  d,  d],
    ])

# Define cube edges by pairs of vertex indices
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # bottom
    (4, 5), (5, 6), (6, 7), (7, 4),  # top
    (0, 4), (1, 5), (2, 6), (3, 7)   # vertical edges
]

# Rotation functions
def rotate_x(points, angle):
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ])
    return points @ R.T

def rotate_y(points, angle):
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ])
    return points @ R.T

def rotate_z(points, angle):
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ])
    return points @ R.T

# Projection from 3D to 2D (orthographic)
def project(points, scale=100, offset=(200, 200)):
    projected = []
    for x, y, z in points:
        # Optional: Add perspective with focal length
        f = 3
        factor = f / (f + z) if z > -f else 1
        x2d = x * scale * factor + offset[0]
        y2d = -y * scale * factor + offset[1]  # Flip Y for screen coordinates
        projected.append((x2d, y2d))
    return projected

# Main draw function
def draw_cube():
    cube = get_cube_vertices(size=1.5)
    angle = 0
    while True:
        canvas.clear()
        rotated = rotate_x(cube, radians(angle))
        rotated = rotate_y(rotated, radians(angle * 1.2))
        rotated = rotate_z(rotated, radians(angle * 0.7))

        projected = project(rotated)

        # Draw edges
        for start, end in edges:
            x1, y1 = projected[start]
            x2, y2 = projected[end]
            canvas.set_stroke_color(0, 0, 1)
            canvas.set_line_width(2)
            canvas.draw_line(x1, y1, x2, y2)

        time.sleep(0.03)
        angle = (angle + 2) % 360

draw_cube()
