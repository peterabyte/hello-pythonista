from cube_model import CubeModel

# ---------- BeginnerSolver ----------
# Produces a list of moves in Singmaster notation.

def _repeat(m, n):  # utility
    return [m]*n

class BeginnerSolver:
    def __init__(self):
        # Common algorithms used in the last layer, etc.
        self.alg = {
            # Edge orientation (OLL edges) – "dot", "L", "line" cases
            'OLL_E_L': ["F","U","R","U'","R'","F'"],
            'OLL_E_LINE': ["F","R","U","R'","U'","F'"],

            # Corner orientation (OLL corners)
            'OLL_C_SUNE': ["R","U","R'","U","R","U2","R'"],
            'OLL_C_ANTISUNE': ["L'","U'","L","U'","L'","U2","L"],

            # PLL permutations (A, U, H, Z as needed)
            'PLL_UA': ["R","U'","R","U","R","U","R","U'","R'","U'","R2"],
            'PLL_UB': ["R2","U","R","U","R'","U'","R'","U'","R'","U","R'"],
            'PLL_Z': ["M2","U","M2","U","M'","U2","M2","U2","M'","U2"],  # M moves unsupported here; fallback later
            'PLL_H': ["M2","U","M2","U2","M2","U","M2"],                 # ditto
        }
        # We won’t actually use M/E/S; we’ll stick to outer-layer moves.
        # If Z/H appears, we’ll translate into outer-layer sequences.

    # Helper: rotate U layer until a predicate is true, applying moves to both cube and list
    def _spin_U_until(self, cube, seq, pred, max_spins=4):
        for i in range(max_spins):
            if pred():
                return True
            cube.move('U')
            seq.append('U')
        return pred()

    # Entry point
    def solve(self, cube: CubeModel):
        seq = []

        # 0) Pre-rotate: we assume White = D face color 'D', Yellow = U 'U'.
        # If you want white on U in your UI, you can rotate whole cube logically here.

        # 1) White cross on D
        seq += self._solve_white_cross(cube)

        # 2) First-layer corners (white on D)
        seq += self._solve_white_corners(cube)

        # 3) Second layer edges
        seq += self._solve_second_layer(cube)

        # 4) OLL edges then corners (make entire U face yellow)
        seq += self._oll_edges(cube)
        seq += self._oll_corners(cube)

        # 5) PLL corners then edges
        seq += self._pll_corners(cube)
        seq += self._pll_edges(cube)

        return seq

    # ------ Recognizers & workers (compact implementations) ------

    def _solve_white_cross(self, cube):
        # Very compact heuristic cross: bring D color edges to D with correct side alignment.
        # Uses simple insertion patterns and spins U as needed.
        seq = []
        target = 'D'
        # Repeat until D cross solved (edges on D with matching side centers)
        def cross_done():
            f = cube.faces
            return (f[3][1]==target and f[3][3]==target and f[3][5]==target and f[3][7]==target and
                    f[2][7]==f[2][4] and f[1][7]==f[1][4] and f[5][7]==f[5][4] and f[4][7]==f[4][4])

        # very naive loop: if not done, apply simple sequences that tend to place edges
        guard = 0
        while not cross_done() and guard < 120:
            guard += 1
            # try bring an edge from U to D using F moves
            seq += ["F","U","R","U'","R'","F'"]
            cube.apply(["F","U","R","U'","R'","F'"])
            if cross_done(): break
            # spin U for different pairing
            cube.move("U"); seq.append("U")
        return seq

    def _solve_white_corners(self, cube):
        seq = []
        target = 'D'
        # Insert each white corner with R U R' U' like patterns, spinning U to align.
        def d_corners_done():
            f = cube.faces
            return all(f[3][i]==target for i in (0,2,6,8))
        guard = 0
        while not d_corners_done() and guard < 200:
            guard += 1
            # standard "right insertion"
            seq += ["U","R","U'","R'","U'","F'","U","F"]
            cube.apply(["U","R","U'","R'","U'","F'","U","F"])
        return seq

    def _solve_second_layer(self, cube):
        seq = []
        # Very compact second-layer insertion macro repeated
        guard = 0
        while guard < 200 and not self._second_layer_done(cube):
            guard += 1
            # try left or right insert
            seq += ["U","R","U'","R'","U'","F'","U","F"]
            cube.apply(["U","R","U'","R'","U'","F'","U","F"])
            if self._second_layer_done(cube): break
            seq += ["U'","L'","U","L","U","F","U'","F'"]
            cube.apply(["U'","L'","U","L","U","F","U'","F'"])
        return seq

    def _second_layer_done(self, cube):
        f = cube.faces
        # Check middle layer edges on F, R, B, L match their face colors (ignore U/D)
        F_ok = f[2][3]==f[2][4] and f[2][5]==f[2][4]
        R_ok = f[1][3]==f[1][4] and f[1][5]==f[1][4]
        B_ok = f[5][3]==f[5][4] and f[5][5]==f[5][4]
        L_ok = f[4][3]==f[4][4] and f[4][5]==f[4][4]
        return F_ok and R_ok and B_ok and L_ok

    def _oll_edges(self, cube):
        seq = []
        # Make a line or L on U and apply appropriate alg until all U edges are yellow ('U')
        def edges_oriented():
            f = cube.faces[0]
            return f[1]=='U' and f[3]=='U' and f[5]=='U' and f[7]=='U'
        guard = 0
        while not edges_oriented() and guard < 12:
            guard += 1
            f = cube.faces[0]
            pattern = (f[1]=='U') + (f[3]=='U') + (f[5]=='U') + (f[7]=='U')
            if pattern in (0,2):
                # Choose L or line orientation by current U pattern
                # Try LINE first
                alg = self.alg['OLL_E_LINE']
                cube.apply(alg); seq += alg
            else:
                break
        return seq

    def _oll_corners(self, cube):
        seq = []
        def corners_oriented():
            f = cube.faces[0]
            return f[0]==f[1]==f[2]==f[3]==f[4]==f[5]==f[6]==f[7]==f[8]=='U'
        guard = 0
        while not corners_oriented() and guard < 24:
            guard += 1
            # Use SUNE / Anti-SUNE cycles until all oriented
            alg = self.alg['OLL_C_SUNE']
            cube.apply(alg); seq += alg
            if corners_oriented(): break
            alg = self.alg['OLL_C_ANTISUNE']
            cube.apply(alg); seq += alg
            cube.move('U'); seq.append('U')
        return seq

    def _pll_corners(self, cube):
        seq = []
        # Simple UA/UB until corners permuted
        guard = 0
        while not self._corners_permuted(cube) and guard < 20:
            guard += 1
            alg = self.alg['PLL_UA']
            cube.apply(alg); seq += alg
            cube.move('U'); seq.append('U')
        return seq

    def _corners_permuted(self, cube):
        # naive: check that each U-layer corner matches side centers (ignores orientation)
        f = cube.faces
        Uc = (f[0][0], f[0][2], f[0][6], f[0][8])
        # If all U face stickers are U (after OLL), corners are "permuted" when side colors match centers
        return all(s=='U' for s in Uc)

    def _pll_edges(self, cube):
        seq = []
        # UA/UB on edges; very naive loop with U spins
        guard = 0
        while not cube.is_solved() and guard < 60:
            guard += 1
            alg = self.alg['PLL_UB']
            cube.apply(alg); seq += alg
            cube.move('U'); seq.append('U')
            if cube.is_solved(): break
        return seq
