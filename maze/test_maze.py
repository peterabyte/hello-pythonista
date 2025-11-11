import unittest
from unittest.mock import MagicMock

from maze_generator import dfs_generate_maze

class MazeTestCase(unittest.TestCase):
  def test_generate_model(self):
    maze_model = dfs_generate_maze(21, 21)
    
    print(maze_model.as_string())

if __name__ == '__main__':
    unittest.main()
