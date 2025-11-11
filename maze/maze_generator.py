from abc import ABC, abstractmethod
import random

from maze_model import MazeModel, CELL_BLOCKED, CELL_FREE

class MazeGenerator(ABC):
  @abstractmethod
  def generate_maze(self, width: int, height: int, cell_blocked: str, cell_free: str) -> MazeModel:
    pass

def dfs_generate_maze(width, height):
  generator = DfsMazeGenerator()
  return generator.generate_maze(width, height, CELL_BLOCKED, CELL_FREE)

class DfsMazeGenerator(MazeGenerator):
  def generate_maze(self, width: int, height: int, cell_blocked: str, cell_free: str) -> MazeModel:
    # Ensure odd dimensions
    assert width % 2 != 0
    assert height % 2 != 0

    maze = [[cell_blocked for _ in range(width)] for _ in range(height)]
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    def carve(y, x):
      maze[y][x] = cell_free
      random.shuffle(directions)
      for dy, dx in directions:
        ny, nx = y + dy, x + dx
        if 1 <= ny < height - 1 and 1 <= nx < width - 1 and maze[ny][nx] == cell_blocked:
          maze[y + dy // 2][x + dx // 2] = cell_free
          carve(ny, nx)

    # Start carving from a random odd cell
    start_y = random.randrange(1, height, 2)
    start_x = random.randrange(1, width, 2)
    carve(start_y, start_x)

    # Choose random entrance and exit on outer walls
    possible_sides = ['top', 'bottom', 'left', 'right']
    entrance_side = random.choice(possible_sides)
    exit_side = random.choice([s for s in possible_sides if s != entrance_side])

    def open_side(side):
      if side == 'top':
        x = random.randrange(1, width, 2)
        maze[0][x] = cell_free
        return (x, 0)
      elif side == 'bottom':
        x = random.randrange(1, width, 2)
        maze[height - 1][x] = cell_free
        return (x, height - 1)
      elif side == 'left':
        y = random.randrange(1, height, 2)
        maze[y][0] = cell_free
        return (0, y)
      elif side == 'right':
        y = random.randrange(1, height, 2)
        maze[y][width - 1] = cell_free
        return (width - 1, y)

    entrance_coords = open_side(entrance_side)
    exit_coords = open_side(exit_side)
  
    maze_model = MazeModel(maze, entrance_coords, exit_coords)
    return maze_model
