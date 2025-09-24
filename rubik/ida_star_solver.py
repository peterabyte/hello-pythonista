from cube_model import CubeModel
import copy

MOVES = [
    'U', "U'", 'U2',
    'D', "D'", 'D2',
    'R', "R'", 'R2',
    'L', "L'", 'L2',
    'F', "F'", 'F2',
    'B', "B'", 'B2'
]

def heuristic(cube: CubeModel):
    # Simple heuristic: count misplaced stickers (not optimal, but admissible)
    count = 0
    for face in cube.faces:
        center = face[4]
        count += sum(1 for s in face if s != center)
    return count // 8  # Dividing to keep heuristic lower (admissible)

def ida_star_solve(start_cube: CubeModel, max_depth=20):
    threshold = heuristic(start_cube)
    path = []
    visited = set()

    def search(cube, g, prev_move):
        f = g + heuristic(cube)
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

    while threshold <= max_depth:
        visited.clear()
        result = search(start_cube, 0, None)
        if result is True:
            return path.copy()
        if result == float('inf'):
            break
        threshold = result
    return None

# Example usage:
# if __name__ == "__main__":
#     cube = CubeModel()
#     scramble = ["R", "U", "R'", "U'"]
#     cube.apply(scramble)
#     solution = ida_star_solve(cube, max_depth=7)
#     print("Scramble:", scramble)
#     print("Solution:", solution)