from scene import run, Scene
from math import floor
from mazes import random_maze, maze
from strategies import keep_left

class MazeAnimation (Scene):
	def setup(self):
		self.background_color = '#82561c'
		#self.maze = random_maze()
		self.maze = maze(3)
		self.maze.setup(self)
		self.strategy = keep_left(self.maze)	
	
	def update(self):
		if self.maze.finished():
			self.game_over = True
		elif not self.maze.player_move():
			direction = self.strategy.where_to_go()
			self.maze.player_go(direction)

if __name__ == '__main__':
	run(MazeAnimation())
