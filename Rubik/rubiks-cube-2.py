import numpy as np
import canvas
import time
from math import radians

# Face colors
FACE_COLORS = {
    'front': (1, 0, 0),     # Red
    'back': (1, 0.5, 0),    # Orange
    'top': (1, 1, 1),       # White
    'bottom': (1, 1, 0),    # Yellow
    'left': (0, 0, 1),      # Blue
    'right': (0, 1, 0),     # Green
}

# Cubelet size
CUBE_SIZE = 0.3

# Create one cubelet’s vertices
def get_cube_vertices(center, size):
    d = size / 2
    c = np.array(center)
    return np.array([
        c + [-d, -d, -d],
        c + [ d, -d, -d],
        c + [ d,  d, -d],
        c + [-d,  d, -d],
        c + [-d, -d,  d],
        c + [ d, -d,  d],
        c + [ d,  d,  d],
        c + [-d,  d,  d],
    ])

# Faces and their names
FACES = [
    ([0, 1, 2, 3], 'back'),
    ([4, 5, 6, 7], 'front'),
    ([0, 1, 5, 4], 'bottom'),
    ([2, 3, 7, 6], 'top'),
    ([1, 2, 6, 5], 'right'),
    ([0, 3, 7, 4], 'left'),
]

# Rotation matrices
def rotate(points, ax, ay, az):
    rx = np.array([
        [1, 0, 0],
        [0, np.cos(ax), -np.sin(ax)],
        [0, np.sin(ax), np.cos(ax)]
    ])
    ry = np.array([
        [np.cos(ay), 0, np.sin(ay)],
        [0, 1, 0],
        [-np.sin(ay), 0, np.cos(ay)]
    ])
    rz = np.array([
        [np.cos(az), -np.sin(az), 0],
        [np.sin(az), np.cos(az), 0],
        [0, 0, 1]
    ])
    return points @ rz.T @ ry.T @ rx.T

# Projection
def project(points, scale=100, offset=(250, 250)):
    result = []
    for x, y, z in points:
        f = 3
        factor = f / (f + z)
        x2d = x * scale * factor + offset[0]
        y2d = -y * scale * factor + offset[1]
        result.append((x2d, y2d))
    return result

def draw_polygon(points_2d):
    if not points_2d:
        return
    canvas.begin_path()
    canvas.move_to(*points_2d[0])
    for pt in points_2d[1:]:
        canvas.add_line(*pt)
    canvas.close_path()
    canvas.fill_path()
    canvas.draw_path()

# Draw one cubelet
def draw_cubelet(center, rotation_angles):
    vertices = get_cube_vertices(center, CUBE_SIZE)
    rotated = rotate(vertices, *rotation_angles)
    projected = project(rotated)

    # Draw visible faces with correct coloring
    for indices, face_name in FACES:
        face_pts_3d = rotated[indices]
        normal = np.cross(face_pts_3d[1] - face_pts_3d[0], face_pts_3d[2] - face_pts_3d[0])
        if normal[2] < 0:  # basic back-face culling
        #if True:
            face_pts_2d = [projected[i] for i in indices]
            canvas.set_fill_color(*FACE_COLORS[face_name])
            canvas.set_stroke_color(0, 0, 0)
            canvas.set_line_width(1)
            draw_polygon(face_pts_2d)

# Main draw loop
def draw_rubiks_cube():
    angle = 0
    while True:
        canvas.clear()
        angle_x = radians(angle)
        angle_y = radians(angle * 0.7)
        angle_z = radians(angle * 0.5)
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    draw_cubelet((x * CUBE_SIZE * 1.1, y * CUBE_SIZE * 1.1, z * CUBE_SIZE * 1.1),
                                 (angle_x, angle_y, angle_z))

        time.sleep(0.03)
        angle = (angle + 1) % 360

draw_rubiks_cube()
