from cube_model import CubeModel
from solver import Solver

MOVES = [
    'U', "U'", 'U2',
    'D', "D'", 'D2',
    'R', "R'", 'R2',
    'L', "L'", 'L2',
    'F', "F'", 'F2',
    'B', "B'", 'B2'
]

class IdaStarSolver(Solver):
    def __init__(self, max_depth=20):
        self.max_depth = max_depth

    def heuristic(self, cube: CubeModel):
        # Simple heuristic: count misplaced stickers (not optimal, but admissible)
        count = 0
        for face in cube.faces:
            center = face[4]
            count += sum(1 for s in face if s != center)
        return count // 8  # Dividing to keep heuristic lower (admissible)

    def solve(self, start_cube: CubeModel) -> list:
        threshold = self.heuristic(start_cube)
        path = []
        visited = set()

        def search(cube, g, prev_move):
            f = g + self.heuristic(cube)
            if f > threshold:
                return f
            if cube.is_solved():
                return True
            min_threshold = float('inf')
            for move in MOVES:
                # Prune consecutive inverse moves
                if prev_move and move[0] == prev_move[0] and move != prev_move:
                    continue
                next_cube = cube.clone()
                next_cube.move(move)
                state_str = next_cube.as_string()
                if state_str in visited:
                    continue
                visited.add(state_str)
                path.append(move)
                result = search(next_cube, g + 1, move)
                if result is True:
                    return True
                if isinstance(result, int) and result < min_threshold:
                    min_threshold = result
                path.pop()
                visited.remove(state_str)
            return min_threshold

        while threshold <= self.max_depth:
            visited.clear()
            result = search(start_cube, 0, None)
            if result is True:
                return path.copy()
            if result == float('inf'):
                break
            threshold = result
        return None
