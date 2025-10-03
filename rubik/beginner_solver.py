from cube_model import CubeModel
from solver import Solver
import logging

# TODO: Implement beginner solver phases.
#       Maybe IDA* solver could be used to find the solution to the specific phases.

class BeginnerSolver(Solver):
    def solve(self, cube: CubeModel) -> list:
        seq = []
        seq += self.solve_white_cross(cube)
        seq += self._solve_white_corners(cube)
        seq += self._solve_second_layer(cube)
        seq += self._solve_oll(cube)
        seq += self._solve_pll(cube)
        return seq

    # --- PHASE 1: White Cross ---
    def solve_white_cross(self, cube):
        logging.info('Solve white-cross on cube: %s', cube.as_string())
        seq = []
        logging.info('Solution (white-cross) cube: "%s"; moves: %s', cube.as_string(), seq)
        return seq

    # --- PHASE 2: White Corners ---
    def _solve_white_corners(self, cube):
        seq = []
        return seq

    # --- PHASE 3: Second Layer Edges ---
    def _solve_second_layer(self, cube):
        seq = []
        return seq

    # --- PHASE 4: OLL (Orient Last Layer) ---
    def _solve_oll(self, cube):
        seq = []
        return seq

    # --- PHASE 5: PLL (Permute Last Layer) ---
    def _solve_pll(self, cube):
        seq = []
        return seq
