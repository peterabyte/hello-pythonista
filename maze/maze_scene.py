from scene import run, Scene
from math import floor

from maze_model import generate_model
from maze_solver import left_hand_on_wall, right_hand_on_wall, random_mouse

MAZE_SIZE_WIDTH = 9
MAZE_SIZE_HEIGHT = 9

class MazeUi:
  pass

class MazeScene (Scene):
  def setup(self):
    self.background_color = '#82561c'
    self.model = generate_model(MAZE_SIZE_WIDTH, MAZE_SIZE_HEIGHT)
    self.ui = MazeUi(self, self.model)
    self.strategy = random_mouse(self.model)	

  def update(self):
    if self.maze.finished():
      self.game_over = True
    elif not self.maze.player_move():
      direction = self.strategy.where_to_go()
      self.maze.player_go(direction)

if __name__ == '__main__':
  maze_scene = MazeScene()
  run(maze_scene)
