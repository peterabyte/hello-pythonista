import ui
import numpy as np
from math import radians, sin, cos
from collections import deque
import random
import logging

from cube_model import CubeModel
from beginner_solver import BeginnerSolver

LOG_LEVEL = logging.DEBUG

CUBE_SIZE = 0.5
CUBE_GAP = 1.01

# Standard Rubik's Cube face colors
FACE_COLORS = {
    'front':  (1, 0, 0),    # Red
    'back':   (1, 0.5, 0),  # Orange
    'top':    (1, 1, 1),    # White
    'bottom': (1, 1, 0),    # Yellow
    'left':   (0, 0, 1),    # Blue
    'right':  (0, 1, 0),    # Green
}
FACE_COLOR_INNER = 'gray'
FACE_COLOR_EDGE = 'black'

FACES = [
    ([0, 1, 2, 3], 'back'),
    ([4, 5, 6, 7], 'front'),
    ([0, 1, 5, 4], 'bottom'),
    ([2, 3, 7, 6], 'top'),
    ([1, 2, 6, 5], 'right'),
    ([0, 3, 7, 4], 'left'),
]

# ---------- UI integration helpers ----------

# Map move notation to: (axis, layer_index, quarter_turns, direction)
# Your cube local axes: x (L/R), y (D/U), z (B/F); layer_index: -1,0,1
# Positive 90° around local axis uses right-hand rule.
MOVE_MAP = {
    'U':  ('y',  1, 1, +1),   "U'": ('y',  1, 1, -1),  'U2': ('y',  1, 2, +1),
    'D':  ('y', -1, 1, -1),   "D'": ('y', -1, 1, +1),  'D2': ('y', -1, 2, +1),
    'R':  ('x',  1, 1, +1),   "R'": ('x',  1, 1, -1),  'R2': ('x',  1, 2, +1),
    'L':  ('x', -1, 1, -1),   "L'": ('x', -1, 1, +1),  'L2': ('x', -1, 2, +1),
    'F':  ('z',  1, 1, +1),   "F'": ('z',  1, 1, -1),  'F2': ('z',  1, 2, +1),
    'B':  ('z', -1, 1, -1),   "B'": ('z', -1, 1, +1),  'B2': ('z', -1, 2, +1),
}

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

class Cube:
    def __init__(self):
        self.global_R = np.identity(3)    # cube's physical orientation in world space
        self.cubelets = [Cubelet((x, y, z)) for x in [-1, 0, 1] for y in [-1, 0, 1] for z in [-1, 0, 1]]
        # handy base offsets for drawing (local cubelet corners)
        d = CUBE_SIZE / 2.0
        self.local_offsets = np.array([
            [-d, -d, -d],    # 0
            [ d, -d, -d],    # 1
            [ d,  d, -d],    # 2
            [-d,  d, -d],    # 3
            [-d, -d,  d],    # 4
            [ d, -d,  d],    # 5
            [ d,  d,  d],    # 6
            [-d,  d,  d],    # 7
        ])
        self.logic = CubeModel()         # logical solver model
        self.solver = BeginnerSolver()   # the solver
        self._move_queue = deque()
        self._current_move = None
        self._remaining = 0
        self._step = 9  # degrees per frame for animation
        self._scrambled = False
        
    def action(self):
        if self._scrambled:
            solution = self.solver.solve(self.logic.clone())
            self.play_moves(self, solution)
            logging.debug('Solve Rubik\'s Cube. solution: %s', solution)
        else:
            length = 20
            tokens = list(MOVE_MAP.keys())
            seq = []
            last_face = ''
            for _ in range(length):
                m = random.choice(tokens)
                # avoid same face twice
                while m[0] == last_face:
                    m = random.choice(tokens)
                last_face = m[0]
                seq.append(m)
            self.play_moves(self, seq)
            # update logical model too:
            self.logic.apply(seq)
            logging.debug('Scramble Rubik\'s Cube. random moves: %s', seq)
        self._scrambled = not self._scrambled
        logging.debug('Update scrmabled state to: %s', self._scrambled)

    def play_moves(self, moves, degrees_per_frame=9):
        logging.debug('Play moves: %s', moves)
        self._move_queue = deque()
        for token in moves:
            axis, layer, q, dir_ = MOVE_MAP[token]
            for _ in range(q):
                # store a 90° turn broken into small steps
                total = 90 * dir_
                self._move_queue.append((axis, layer, total))
        self._current_move = None
        self._remaining = 0
        self._step = degrees_per_frame

    def rotate_cube(self, axis, angle_rad):
        R = self.rotation_matrix(axis, angle_rad)
        self.global_R = R @ self.global_R
        for c in self.cubelets:
            c.rotate(R)

    def update(self):
        if self._current_move is None and self._move_queue:
            self._current_move = self._move_queue.popleft()
            self._remaining = abs(self._current_move[2])

        if self._current_move:
            axis, layer, total_deg = self._current_move
            step = min(self._step, self._remaining)
            angle = radians(step if total_deg > 0 else -step)
            self.rotate_slice(axis, layer, angle)
            self._remaining -= step
            if self._remaining <= 0:
                token = self.last_token_from_move(axis, layer, total_deg)
                if token:
                    self.logic.move(token)
                self._current_move = None

        return (self._current_move, len(self._move_queue))

    def last_token_from_move(self, axis, layer, total_deg):
        # Convert (axis,layer,±90) to token (U,D,L,R,F,B or their primes).
        if abs(total_deg) != 90: return None
        # Map local axis+layer+direction to notation
        if axis == 'y' and layer ==  1: return "U"  if total_deg>0 else "U'"
        if axis == 'y' and layer == -1: return "D'" if total_deg>0 else "D"
        if axis == 'x' and layer ==  1: return "R"  if total_deg>0 else "R'"
        if axis == 'x' and layer == -1: return "L'" if total_deg>0 else "L"
        if axis == 'z' and layer ==  1: return "F"  if total_deg>0 else "F'"
        if axis == 'z' and layer == -1: return "B'" if total_deg>0 else "B"
        return None

    def rotate_slice(self, axis, layer_index, angle_rad):
        # 1. Local axis unit vector (cube space)
        local_axis = np.zeros(3)
        local_axis[['x', 'y', 'z'].index(axis)] = 1.0

        # 2. Convert to world axis using the cube’s global rotation
        world_axis = self.global_R @ local_axis

        # 3. Build rotation matrix around this axis
        R = self.rotation_matrix_from_vector(world_axis, angle_rad)

        # 4. For each cubelet, check if it's in the slice (by projection onto local axis)
        spacing = CUBE_SIZE * CUBE_GAP
        for cubelet in self.cubelets:
            # Project center into cube-local coordinates
            local_center = np.linalg.inv(self.global_R) @ cubelet.center
            coord = round(local_center[['x','y','z'].index(axis)] / spacing)
            if coord == layer_index:
                # Rotate in world coordinates
                cubelet.center = R @ cubelet.center
                cubelet.rotation = R @ cubelet.rotation

    def project(self, points, scale=100, offset=(0, 0)):
        result = []
        for x, y, z in points:
            f = 3
            factor = f / (f + z)
            x2d = x * scale * factor + offset[0]
            y2d = -y * scale * factor + offset[1]
            result.append((x2d, y2d))
        return result

    def rotation_matrix(self, axis, theta):
        c, s = cos(theta), sin(theta)
        if axis == 'x':
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == 'y':
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == 'z':
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    def rotation_matrix_from_vector(self, axis_vec, theta):
        """Rotation matrix for arbitrary axis (Rodrigues)."""
        axis_vec = axis_vec / np.linalg.norm(axis_vec)
        x, y, z = axis_vec
        c, s = cos(theta), sin(theta)
        C = 1 - c
        return np.array([
            [c + x*x*C,     x*y*C - z*s, x*z*C + y*s],
            [y*x*C + z*s, c + y*y*C,     y*z*C - x*s],
            [z*x*C - y*s, z*y*C + x*s, c + z*z*C]
        ])

    def faces_to_draw(self, offset=(0, 0)):
        all_faces = []
        for c in self.cubelets:
            # Build cubelet vertices in WORLD space:
            # rotate local offsets by the cubelet's own orientation, then translate by center
            verts_world = (self.local_offsets @ c.rotation.T) + c.center

            # We now draw in world coords (no extra global_R here, since we rotate the cube physically)
            projected = self.project(verts_world, offset=offset)

            x, y, z = c.grid_pos
            visible_faces = {
                'back':     (z == -1),
                'front':    (z ==  1),
                'left':     (x == -1),
                'right':    (x ==  1),
                'bottom':   (y == -1),
                'top':      (y ==  1)
            }

            for indices, face_name in FACES:
                face_color = FACE_COLORS[face_name]
                if not visible_faces[face_name]:
                    face_color = FACE_COLOR_INNER

                face3d = verts_world[indices]
                face2d = [projected[i] for i in indices]
                avg_depth = float(np.mean(face3d[:, 2]))
                all_faces.append((avg_depth, face2d, face_color, face3d))

        # Painter's algorithm with stable tie-breakers to avoid flicker
        all_faces.sort(
            key=lambda f: (round(f[0], 6), round(np.min(f[3][:,0]), 6), round(np.min(f[3][:,1]), 6)),
            reverse=True
        )
        return all_faces

    def state(self):
        state = {}
        for c in self.cubelets:
            x, y, z = c.grid_pos
            key = (x, y, z)
            state[key] = {}
            for indices, face_name in FACES:
                if ((face_name == 'front' and z == 1) or
                    (face_name == 'back' and z == -1) or
                    (face_name == 'left' and x == -1) or
                    (face_name == 'right' and x == 1) or
                    (face_name == 'top' and y == 1) or
                    (face_name == 'bottom' and y == -1)):
                    state[key][face_name] = FACE_COLORS[face_name]
        return state

class ActionButton:
    def __init__(self, view, click):
        self.btn = ui.Button(
            title='Scramble',
            bg_color='#55bcff',
            tint_color='#fff',
            corner_radius=9,
            action=click
        )
        self.btn.center = (60, 40)
        self.btn.height = 50
        self.btn.width = 160
        self._main_title = 'Scramble'
        view.add_subview(self.btn)

    def disable(self):
        logging.debug("Disable button")
        self.btn.enabled = False

    def enable(self):
        logging.debug("Enable button")
        self.btn.enabled = True

    def update_main_title(self, main_title):
        logging.debug('Update button title to: %s', main_title)
        self._main_title = main_title
        self.btn.title = self._main_title

    def set_sub_title(self, sub_title):
        logging.debug('Set sub title to: %s', sub_title)
        self.btn.title = self._main_title + ': ' + sub_title

class RubiksCubeView (ui.View):
    def __init__(self):
        self.flex = 'WH'
        self.update_interval = 0.05
        self.btn = ActionButton(self, self.action_click)
        self.cube = Cube()
        self._waiting_idle = False

    def action_click(self, sender):
        self.btn.disable()
        self.cube.action()

    # Rotate the WHOLE cube physically around a world axis
    def rotate_cube(self, axis, angle_rad):
        self.cube.rotate_cube(axis, angle_rad)

    def update(self):
        current_move, remaining_num_of_moves = self.cube.update()
        self.update_button(current_move, remaining_num_of_moves)
        self.set_needs_display()

    def update_button(self, current_move, remaining_num_of_moves):
        if current_move is None:
            if remaining_num_of_moves >= 0:
                self._waiting_idle = False
                self.btn.set_sub_title(str(remaining_num_of_moves))
            else:
                if not self._waiting_idle:
                    self._waiting_idle = True
                    self.btn.enable()
                    title = 'Solve' if self._scrambled else 'Scramble'
                    self.btn.update_main_title(title)

    def draw(self):
        all_faces = self.cube.faces_to_draw(
            offset=(self.width / 2, self.height / 2)
        )
        for _, pts, color, _ in all_faces:
            self.draw_poly(pts, color)

    def draw_poly(self, pts, color):
        path = ui.Path()
        path.move_to(*pts[0])
        for pt in pts[1:]:
            path.line_to(*pt)
        path.close()
        ui.set_color(color)
        path.fill()
        ui.set_color(FACE_COLOR_EDGE)
        path.stroke()

logging.basicConfig(level=LOG_LEVEL)

rubiks_view = RubiksCubeView()
rubiks_view.rotate_cube('y', radians(35))
rubiks_view.rotate_cube('x', radians(-25))
rubiks_view.present(style='full_screen', animated=False, hide_title_bar=True)

