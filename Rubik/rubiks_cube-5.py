import scene
import ui
import numpy as np
from math import radians, sin, cos

CUBE_SIZE = 0.3
CUBE_GAP = 1.01

# Standard Rubik's Cube face colors
FACE_COLORS = {
  'front': (1, 0, 0),   # Red
  'back': (1, 0.5, 0),  # Orange
  'top': (1, 1, 1),     # White
  'bottom': (1, 1, 0),  # Yellow
  'left': (0, 0, 1),    # Blue
  'right': (0, 1, 0),   # Green
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

def project(points, scale=100, offset=(300, 400)):
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

def draw_poly(pts, color):
  path = ui.Path()
  path.move_to(*pts[0])
  for pt in pts[1:]:
    path.line_to(*pt)
  path.close()
  ui.set_color(color)
  path.fill()
  ui.set_color('black')
  path.stroke()

class Cubelet:
  def __init__(self, pos):
    self.grid_pos = np.array(pos)
    self.center = self.grid_pos * CUBE_SIZE * CUBE_GAP
    self.rotation = np.identity(3)

  def rotate(self, axis, angle_rad):
    R = rotation_matrix(axis, angle_rad)
    self.center = R @ self.center
    self.rotation = R @ self.rotation

  def finalize_rotation(self):
    self.grid_pos = np.round(self.center / (CUBE_SIZE * 1.1)).astype(int)
    self.center = self.grid_pos * CUBE_SIZE * CUBE_GAP

class RubiksView (ui.View):
  def __init__(self):
    self.background_color = (0.5, 0.5, 0.5)
    self.flex = 'WH'
    self.update_interval = 0.05
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

#    if self.rotating:
#      delta = radians(6)
#      self.slice_rotation_angle += delta
#      if self.slice_rotation_angle >= radians(90):
#        delta -= (self.slice_rotation_angle - radians(90))
#        self.rotating = False
#      for c in self.cubelets:
#        if c.grid_pos[1] == self.layer:
#          c.rotate(self.axis, delta)
#      if not self.rotating:
#        for c in self.cubelets:
#          if c.grid_pos[1] == self.layer:
#            c.finalize_rotation()
    self.rotate_slice('x', 1, radians(6))

    self.set_needs_display()

  def rotate_slice(self, axis, layer_index, angle_rad):
    """
    Rotate a single slice of the cube around one axis.

    axis: 'x', 'y', or 'z'
    layer_index: -1, 0, or 1 (grid position along that axis)
    angle_rad: rotation angle in radians (positive = clockwise when looking along +axis)
    """
    # Build rotation matrix
    R = rotation_matrix(axis, angle_rad)

    # Which coordinate index to check
    axis_index = {'x': 0, 'y': 1, 'z': 2}[axis]

    for cubelet in self.cubelets:
      if cubelet.grid_pos[axis_index] == layer_index:
        # 1) Rotate center in world coordinates
        cubelet.center = R @ cubelet.center

        # 2) Rotate orientation matrix
        cubelet.rotation = R @ cubelet.rotation
        cubelet.finalize_rotation()

    # Optional: snap to grid after small rotations to avoid floating-point drift
#    for cubelet in self.cubelets:
#      cubelet.grid_pos = np.round(cubelet.center / self.spacing).astype(int)
#      cubelet.center = cubelet.grid_pos * self.spacing

  def draw(self):
    all_faces = []
    for cubelet in self.cubelets:
      verts = get_cube_vertices(cubelet.center, CUBE_SIZE)
      transformed = (verts @ cubelet.rotation.T) @ self.global_R.T
      projected = project(transformed)

      view_dir = np.array([0, 0, -1])
      view_dir_world = self.global_R @ view_dir

      x, y, z = cubelet.grid_pos

      visible_faces = {
        'back':   (z == -1),
        'front':  (z ==  1),
        'left':   (x == -1),
        'right':  (x ==  1),
        'bottom': (y == -1),
        'top':    (y ==  1)
      }

      for indices, face_name in FACES:
        if not visible_faces[face_name]:
          continue

        face_pts_3d = transformed[indices]
        v1 = face_pts_3d[1] - face_pts_3d[0]
        v2 = face_pts_3d[2] - face_pts_3d[0]
        normal = np.cross(v1, v2)

        #if np.dot(normal, view_dir_world) <= 0:
        if True:
          face_pts_2d = [projected[i] for i in indices]
          avg_depth = np.mean([face_pts_3d[i][2] for i in range(len(face_pts_3d))])
          all_faces.append((avg_depth, face_pts_2d, FACE_COLORS[face_name]))

    # Sort by depth (furthest first)
    all_faces.sort(key=lambda f: f[0], reverse=True)
    # Draw
    for _, pts, color in all_faces:
        draw_poly(pts, color)

rubiks_view = RubiksView()
#Because hide_title_bar is set to True
# the view can be closed with a 2-finger swipe-down gesture. 
rubiks_view.present(style='full_screen', animated=False, hide_title_bar=True)

