from scene import *
import numpy as np
from math import radians, sin, cos

CUBE_SIZE = 0.3

# Standard Rubik's Cube face colors
FACE_COLORS = {
    'front': (1, 0, 0),     # Red
    'back': (1, 0.5, 0),    # Orange
    'top': (1, 1, 1),       # White
    'bottom': (1, 1, 0),    # Yellow
    'left': (0, 0, 1),      # Blue
    'right': (0, 1, 0),     # Green
}

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

def project(points, scale=100, offset=(375, 400)):
    result = []
    for x, y, z in points:
        f = 3
        factor = f / (f + z)
        x2d = x * scale * factor + offset[0]
        y2d = -y * scale * factor + offset[1]
        result.append((x2d, y2d))
    return result

def rotation_matrix(axis, theta):
    c, s = cos(theta), sin(theta)
    if axis == 'x':
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    elif axis == 'y':
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    elif axis == 'z':
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

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

    def draw_poly(self, pts, color):
        path = ui.Path()
        path.move_to(*pts[0])
        for pt in pts[1:]:
            path.line_to(*pt)
        path.close()
        ui.set_color(color)
        stroke('white')
        path.fill()
        path.stroke()

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
            #if np.dot(normal, view_dir_world) < 0:
            if True:
                face_pts_2d = [projected[i] for i in indices]
                self.draw_poly(face_pts_2d, FACE_COLORS[face_name])

class RubiksScene(Scene):
    def setup(self):
        self.angle = 0
        self.global_R = np.identity(3)
        self.slice_rotation_angle = 0
        self.rotating = False
        self.axis = 'y'
        self.layer = 1
        self.cubelets = [Cubelet((x, y, z)) for x in [-1, 0, 1] for y in [-1, 0, 1] for z in [-1, 0, 1]]

    def update(self):
        self.angle += 2
        self.global_R = rotation_matrix('y', radians(self.angle))

        if self.rotating:
            delta = radians(6)
            self.slice_rotation_angle += delta
            if self.slice_rotation_angle >= radians(90):
                delta -= (self.slice_rotation_angle - radians(90))
                self.rotating = False
            for c in self.cubelets:
                if c.grid_pos[1] == self.layer:
                    c.rotate(self.axis, delta)
            if not self.rotating:
                for c in self.cubelets:
                    if c.grid_pos[1] == self.layer:
                        c.finalize_rotation()

    def draw(self):
        background(0.5, 0.5, 0.5)
        self.draw_cubelets()

    def draw_cubelets(self):
        for c in self.cubelets:
            c.draw(self.global_R)

run(RubiksScene(), orientation=PORTRAIT, show_fps=False)
