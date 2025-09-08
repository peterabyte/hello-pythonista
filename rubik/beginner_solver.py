from cube_model import CubeModel

# ---------- BeginnerSolver ----------
# Produces a list of moves in Singmaster notation.

class BeginnerSolver:
    def __init__(self):
        pass

    def solve(self, cube: CubeModel):
        seq = []
        seq += self._solve_white_cross(cube)
        seq += self._solve_white_corners(cube)
        # TODO: uncomment and implement solver
        # seq += self._solve_second_layer(cube)
        # seq += self._solve_oll(cube)
        # seq += self._solve_pll(cube)
        return seq

    # --- PHASE 1: White Cross ---
    def _solve_white_cross(self, cube):
        seq = []
        # For each white edge, bring it to D face with correct orientation
        # White = 'U', so we want D face edges to be 'U' and side stickers to match centers
        # Edges: (D, positions 1,3,5,7)
        for _ in range(4):
            # Find a white edge not solved
            for face in range(6):
                for idx in [1,3,5,7]:
                    color = cube.faces[face][idx]
                    if color == 'U':
                        # If already solved, skip
                        if face == 3 and cube.faces[3][idx] == 'U':
                            continue
                        # If on U face, bring down
                        if face == 0:
                            # U edge: move to D using F2, R2, B2, L2
                            if idx == 1: moves = ['F2']
                            elif idx == 3: moves = ['L2']
                            elif idx == 5: moves = ['R2']
                            elif idx == 7: moves = ['B2']
                            cube.apply(moves); seq += moves
                        # If on side face, bring to U then down
                        elif face in [1,2,4,5]:
                            # Move edge to U
                            if idx == 1: moves = ['D']
                            elif idx == 3: moves = ['D\'']
                            elif idx == 5: moves = ['D2']
                            else: moves = []
                            cube.apply(moves); seq += moves
                            cube.apply(['F2']); seq += ['F2']
                        # If on D but misoriented, flip with F, R, B, L
                        elif face == 3:
                            if idx == 1: moves = ['F', 'D', 'R', 'D\'', 'R\'', 'F\'']
                            elif idx == 3: moves = ['L', 'D', 'F', 'D\'', 'F\'', 'L\'']
                            elif idx == 5: moves = ['R', 'D', 'B', 'D\'', 'B\'', 'R\'']
                            elif idx == 7: moves = ['B', 'D', 'L', 'D\'', 'L\'', 'B\'']
                            cube.apply(moves); seq += moves
        return seq

    # --- PHASE 2: White Corners ---
    def _solve_white_corners(self, cube):
        seq = []
        # Insert each white corner into D layer
        for _ in range(4):
            # Find unsolved white corner
            for face in range(6):
                for idx in [0,2,6,8]:
                    color = cube.faces[face][idx]
                    if color == 'U':
                        # If already solved, skip
                        if face == 3 and cube.faces[3][idx] == 'U':
                            continue
                        # If on U face, use R U R' U' or L' U' L U
                        if face == 0:
                            if idx == 0: moves = ['L\'', 'D\'', 'L', 'D']
                            elif idx == 2: moves = ['R', 'D', 'R\'', 'D\'']
                            elif idx == 6: moves = ['L', 'D', 'L\'', 'D\'']
                            elif idx == 8: moves = ['R\'', 'D\'', 'R', 'D']
                            cube.apply(moves); seq += moves
                        # If on side face, bring to U then insert
                        elif face in [1,2,4,5]:
                            moves = ['D']
                            cube.apply(moves); seq += moves
                            cube.apply(['R', 'D', 'R\'', 'D\'']); seq += ['R', 'D', 'R\'', 'D\'']
                        # If on D but misoriented, use F D F'
                        elif face == 3:
                            moves = ['F', 'U', 'F\'']
                            cube.apply(moves); seq += moves
        return seq

    # --- PHASE 3: Second Layer Edges ---
    def _solve_second_layer(self, cube):
        seq = []
        # For each edge in U layer not containing yellow, insert into second layer
        for _ in range(4):
            for face in [1,2,4,5]:  # R, F, L, B
                # Find edge in U layer
                for idx in [1,3,5,7]:
                    color = cube.faces[0][idx]
                    if color != 'D':
                        # Insert left or right
                        if face == 1: moves = ['D', 'R', 'D\'', 'R\'', 'D\'', 'F\'', 'D', 'F']
                        elif face == 4: moves = ['D\'', 'L\'', 'D', 'L', 'D', 'F', 'D\'', 'F\'']
                        else: moves = []
                        cube.apply(moves); seq += moves
        return seq

    # --- PHASE 4: OLL (Orient Last Layer) ---
    def _solve_oll(self, cube):
        seq = []
        # Orient U face to all yellow ('D')
        # First edges, then corners
        # Edges
        for _ in range(3):
            f = cube.faces[0]
            if not (f[1]=='D' and f[3]=='D' and f[5]=='D' and f[7]=='D'):
                moves = ['F', 'R', 'D', 'R\'', 'D\'', 'F\'']
                cube.apply(moves); seq += moves
        # Corners
        for _ in range(4):
            f = cube.faces[0]
            if not all(f[i]=='D' for i in [0,2,6,8]):
                moves = ['R', 'D', 'R\'', 'D', 'R', 'D2', 'R\'']
                cube.apply(moves); seq += moves
        return seq

    # --- PHASE 5: PLL (Permute Last Layer) ---
    def _solve_pll(self, cube):
        seq = []
        # Permute corners
        for _ in range(4):
            f = cube.faces[0]
            if not all(f[i]=='D' for i in [0,2,6,8]):
                moves = ['R', 'D\'', 'R', 'D', 'R', 'D', 'R', 'D\'', 'R\'', 'D\'', 'R2']
                cube.apply(moves); seq += moves
        # Permute edges
        for _ in range(4):
            if not cube.is_solved():
                moves = ['R2', 'D', 'R', 'D', 'R\'', 'D\'', 'R\'', 'D\'', 'R\'', 'D', 'R\'']
                cube.apply(moves); seq += moves
        return seq
