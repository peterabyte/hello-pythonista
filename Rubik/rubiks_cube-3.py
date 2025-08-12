import numpy as np
import canvas
import time
from math import radians, sin, cos

CUBE_SIZE = 0.3

# Colors for each face
FACE_COLORS = {
    'front': (1, 0, 0),     # Red
    'back': (1, 0.5, 0),    # Orange
    'top': (1, 1, 1),       # White
    'bottom': (1, 1, 0),    # Yellow
    'left': (0, 0, 1),      # Blue
    'right': (0, 1, 0),     # Green
}

# Define faces with vertex indices and names
FACES = [
    ([0, 1, 2, 3], 'back'),
    ([4, 5, 6, 7], 'front'),
    ([0, 1, 5, 4], 'bottom'),
    ([2, 3, 7, 6], 'top'),
    ([1, 2, 6, 5], 'right'),
    ([0, 3, 7, 4], 'left'),
]

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

# Projection function
def project(points, scale=100, offset=(250, 250)):
    result = []
    for x, y, z in points:
        f = 3
        factor = f / (f + z)
        x2d = x * scale * factor + offset[0]
        y2d = -y * scale * factor + offset[1]
        result.append((x2d, y2d))
    return result

# Cubelet class
class Cubelet:
    def __init__(self, pos):
        self.grid_pos = np.array(pos)
        self.center = self.grid_pos * CUBE_SIZE * 1.1
        self.rotation = np.identity(3)

    def rotate(self, axis, angle_rad):
        R = rotation_matrix(axis, angle_rad)
        self.center = R @ self.center
        self.rotation = R @ self.rotation

    def finalize_rotation(self):
        self.grid_pos = np.round(self.center / (CUBE_SIZE * 1.1)).astype(int)
        self.center = self.grid_pos * CUBE_SIZE * 1.1

    def draw_polygon(self, points_2d):
        if not points_2d:
            return
        canvas.begin_path()
        canvas.move_to(*points_2d[0])
        for pt in points_2d[1:]:
            canvas.add_line(*pt)
        canvas.close_path()
        canvas.fill_path()
        canvas.draw_path()

    def draw(self, global_rotation):
        verts = get_cube_vertices(self.center, CUBE_SIZE)
        transformed = (verts @ self.rotation.T) @ global_rotation.T
        projected = project(transformed)

        view_dir = np.array([0, 0, -1])
        view_dir_world = global_rotation @ view_dir  # Transform to match world orientation

        for indices, face_name in FACES:
            face_pts_3d = transformed[indices]
            v1 = face_pts_3d[1] - face_pts_3d[0]
            v2 = face_pts_3d[2] - face_pts_3d[0]
            normal = np.cross(v1, v2)

            # Check if face is facing the camera
            if np.dot(normal, view_dir_world) < 0:
                face_pts_2d = [projected[i] for i in indices]
                canvas.set_fill_color(*FACE_COLORS[face_name])
                canvas.set_stroke_color(1, 1, 1)
                canvas.set_line_width(3)
                self.draw_polygon(face_pts_2d)

# Rotation matrix around X/Y/Z
def rotation_matrix(axis, theta):
    c, s = cos(theta), sin(theta)
    if axis == 'x':
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    elif axis == 'y':
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    elif axis == 'z':
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

# Build all cubelets
def build_cube():
    cubelets = []
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            for z in [-1, 0, 1]:
                cubelets.append(Cubelet((x, y, z)))
    return cubelets

# Main drawing with slice rotation
def draw_rubiks_cube():
    cubelets = build_cube()
    global_angle = 0
    slice_rotation_angle = 0
    #rotating = True
    rotating = False
    axis = 'y'
    layer = 1  # top layer (y = 1)

    while True:
        canvas.clear()
        global_angle += 2
        global_R = rotation_matrix('y', radians(global_angle))

        # Animate one slice rotation
        if rotating:
            delta = radians(6)
            slice_rotation_angle += delta
            if slice_rotation_angle >= radians(90):
                delta -= (slice_rotation_angle - radians(90))
                rotating = False
            for c in cubelets:
                if c.grid_pos[1] == layer:
                    c.rotate(axis, delta)
            if not rotating:
                for c in cubelets:
                    if c.grid_pos[1] == layer:
                        c.finalize_rotation()

        for c in cubelets:
            c.draw(global_R)

        #canvas.update()
        time.sleep(0.03)

draw_rubiks_cube()
