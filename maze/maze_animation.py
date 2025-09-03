from scene import run, Scene
from math import floor
from mazes import maze
from strategies import left_hand, right_hand, random_mouse

class MazeAnimation (Scene):
	def setup(self):
		self.background_color = '#82561c'
		self.maze = maze()
		self.maze.setup(self)
		self.strategy = random_mouse(self.maze)	
	
	def update(self):
		if self.maze.finished():
			self.game_over = True
		elif not self.maze.player_move():
			direction = self.strategy.where_to_go()
			self.maze.player_go(direction)

if __name__ == '__main__':
	run(MazeAnimation())
