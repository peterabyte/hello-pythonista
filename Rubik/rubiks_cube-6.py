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

def rotation_matrix_from_vector(axis_vec, theta):
  """Rotation matrix for arbitrary axis (Rodrigues)."""
  axis_vec = axis_vec / np.linalg.norm(axis_vec)
  x, y, z = axis_vec
  c, s = cos(theta), sin(theta)
  C = 1 - c
  return np.array([
    [c + x*x*C,   x*y*C - z*s, x*z*C + y*s],
    [y*x*C + z*s, c + y*y*C,   y*z*C - x*s],
    [z*x*C - y*s, z*y*C + x*s, c + z*z*C]
  ])

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

  # Rotate by a given 3x3 rotation matrix in world space
  def rotate(self, R):
    self.center = R @ self.center
    self.rotation = R @ self.rotation

  def finalize_rotation(self):
    # snap using the actual spacing (size * gap)
    spacing = CUBE_SIZE * CUBE_GAP
    self.grid_pos = np.round(self.center / spacing).astype(int)
    self.center = self.grid_pos * spacing

class RubiksView (ui.View):
  def __init__(self):
    self.background_color = (0.5, 0.5, 0.5)
    self.flex = 'WH'
    self.update_interval = 0.05
    self.global_R = np.identity(3)  # cube's physical orientation in world space
    self.cubelets = [Cubelet((x, y, z)) for x in [-1, 0, 1]
                                         for y in [-1, 0, 1]
                                         for z in [-1, 0, 1]]

    # handy base offsets for drawing (local cubelet corners)
    d = CUBE_SIZE / 2.0
    self.local_offsets = np.array([
      [-d, -d, -d],  # 0
      [ d, -d, -d],  # 1
      [ d,  d, -d],  # 2
      [-d,  d, -d],  # 3
      [-d, -d,  d],  # 4
      [ d, -d,  d],  # 5
      [ d,  d,  d],  # 6
      [-d,  d,  d],  # 7
    ])

  # Rotate the WHOLE cube physically around a world axis
  def rotate_cube(self, axis, angle_rad):
    R = rotation_matrix(axis, angle_rad)
    self.global_R = R @ self.global_R
    for c in self.cubelets:
      c.rotate(R)

  def update(self):
    # Physically rotate the cube a bit around both X and Y each frame
    self.rotate_cube('y', radians(2))
    self.rotate_cube('x', radians(1))

    # Example: rotate the top layer (y = +1) around cube's local Z axis
    # You can change axis/layer/angle for testing
    self.rotate_slice('z', 1, radians(6))

    self.set_needs_display()

  def rotate_slice(self, axis, layer_index, angle_rad):
    """
    Rotate a slice around the cube's OWN axis (not world axes).
    axis: 'x' | 'y' | 'z'  -> cube-local axis
    layer_index: -1, 0, 1  -> which layer along that axis in cube-local coords
    """
    axis_index_map = {'x': 0, 'y': 1, 'z': 2}
    ax = axis_index_map[axis]

    # Cube-local axis unit vector -> world axis via the cube's current orientation
    local_axis = np.zeros(3)
    local_axis[ax] = 1.0
    world_axis = self.global_R @ local_axis  # rotate local axis into world space

    # Build rotation about that world axis
    R = rotation_matrix_from_vector(world_axis, angle_rad)

    # Rotate only the selected layer (membership defined in cube-local grid coords)
    for c in self.cubelets:
      if c.grid_pos[ax] == layer_index:
        c.rotate(R)

    # NOTE: call c.finalize_rotation() for those cubelets AFTER a full 90° turn completes

  def draw(self):
    all_faces = []

    for c in self.cubelets:
      # Build cubelet vertices in WORLD space:
      # rotate local offsets by the cubelet's own orientation, then translate by center
      verts_world = (self.local_offsets @ c.rotation.T) + c.center

      # We now draw in world coords (no extra global_R here, since we rotate the cube physically)
      projected = project(verts_world)

      x, y, z = c.grid_pos
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

        face3d = verts_world[indices]
        face2d = [projected[i] for i in indices]
        avg_depth = float(np.mean(face3d[:, 2]))
        all_faces.append((avg_depth, face2d, FACE_COLORS[face_name], face3d))

    # Painter's algorithm with stable tie-breakers to avoid flicker
    all_faces.sort(key=lambda f: (round(f[0], 6),
                                  round(np.min(f[3][:,0]), 6),
                                  round(np.min(f[3][:,1]), 6)),
                   reverse=True)

    for _, pts, color, _ in all_faces:
      draw_poly(pts, color)

rubiks_view = RubiksView()
rubiks_view.present(style='full_screen', animated=False, hide_title_bar=True)
