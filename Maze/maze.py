from scene import *
from math import floor
from collections import deque

maze_map = [
	[1, 1, 0, 1, 1],
	[1, 1, 0, 0, 1],
	[1, 1, 1, 0, 1],
	[1, 0, 0, 0, 1],
	[1, 0, 1, 1, 1]
]
maze_textures = [
	'plf:Ground_GrassCenter',
	'plf:Ground_StoneCenter'
]
maze_start = (4, 1)
maze_finish = (0, 2)
step_count_max = 64
image_size = 64
player_offset = 16

class Game (Scene):
	def setup(self):
		self.background_color = '#82561c'
		self.scale = self.calculate_scale()
		self.setup_maze(self.scale)
		self.setup_finish(self.scale)
		self.setup_player(self.scale)
		self.setup_strategy()
	
	def setup_maze(self, scale):
		self.maze_gps = [None] * len(maze_map)
		corner = self.calculate_corner(scale)
		original_x = corner[0]
		x = corner[0]
		y = corner[1]
		for i in range(len(maze_map) - 1, -1, -1):
			self.maze_gps[i] = [None] * len(maze_map[i])
			for j in range(len(maze_map[i])):
				texture = maze_textures[maze_map[i][j]]
				maze_sprite = SpriteNode(texture)
				maze_sprite.anchor_point = (0, 0)
				maze_sprite.position = (x, y)
				maze_sprite.scale = scale
				self.add_child(maze_sprite)
				self.maze_gps[i][j] = (x, y)
				x = x + (scale * image_size)
			x = original_x
			y = y + (scale * image_size)
	
	def setup_finish(self, scale):
		finish = SpriteNode('plf:Item_CoinGold')
		finish.anchor_point = (0, 0)
		finish.position = self.maze_gps[maze_finish[0]][maze_finish[1]]
		finish.scale = scale
		self.add_child(finish)
		
	def setup_player(self, scale):
		self.player = SpriteNode('plf:HudPlayer_beige')
		self.player.anchor_point = (0, 0)
		self.player.position = self.maze_gps[maze_start[0]][maze_start[1]]
		self.player.scale = scale
		self.add_child(self.player)
		self.step_count = None
		self.prev_gps = None
		self.current_gps = maze_start
	
	def setup_strategy(self):
		self.directions = [self.back, self.left, self.straight, self.right]
		self.direction_orientation = {
			"left": [self.back, self.left, self.straight, self.right],
			"straight": [self.left, self.straight, self.right, self.back],
			"right": [self.straight, self.right, self.back, self.left],
			"back": [self.right, self.back, self.left, self.straight]
		}
	
	def calculate_scale(self):
		scale = self.size.w / (image_size * len(maze_map[0]))
		return 1.0 if scale > 1.0 else round(scale, 1)
	
	def calculate_corner(self, scale):
		x = (self.size.w / 2) - (len(maze_map[0]) / 2 * image_size * scale)
		y = (self.size.h / 2) - (len(maze_map) / 2 * image_size * scale)
		return (x, y)
	
	def update(self):
		self.update_player()
	
	def update_player(self):
		if self.is_finished():
			self.game_over = True
		elif self.step_count is None:
			self.go_to_gps = self.where_to_go()
			self.step_count = 0
		elif self.step_count == step_count_max:
			self.step_count = None
		else:
			self.go()
			
	def is_finished(self):
		return self.current_gps == maze_finish
			
	def go(self):
		self.step_count = self.step_count + 1
		if self.step_count < step_count_max:
			x = self.maze_gps[self.current_gps[0]][self.current_gps[1]][0] + ((self.go_to_gps[1] - self.current_gps[1]) * (self.step_count / step_count_max * image_size * self.scale))
			y = self.maze_gps[self.current_gps[0]][self.current_gps[1]][1] + ((self.current_gps[0] - self.go_to_gps[0]) * (self.step_count / step_count_max * image_size * self.scale))
			self.player.position = (x, y)
		else:
			self.prev_gps = self.current_gps
			self.current_gps = self.go_to_gps
			self.player.position = self.maze_gps[self.go_to_gps[0]][self.go_to_gps[1]]
	
	def where_to_go(self):
		for d in list(self.directions):
			direction = d()
			if self.can_go(direction):
				self.directions = self.direction_orientation[d.__name__]
				return direction
		return None
	
	def straight(self):
		return (self.current_gps[0] - 1, self.current_gps[1])
	
	def left(self):
		return (self.current_gps[0], self.current_gps[1] - 1)
	
	def right(self):
		return (self.current_gps[0], self.current_gps[1] + 1)
	
	def back(self):
		return (self.current_gps[0] + 1, self.current_gps[1])
	
	def can_go(self, gps):
		return gps[0] < len(maze_map) and gps[1] < len(maze_map[gps[0]]) and maze_map[gps[0]][gps[1]] == 0
	
if __name__ == '__main__':
	run(Game(), PORTRAIT, show_fps=True)
