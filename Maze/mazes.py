from scene import Scene, SpriteNode
import random
from enum import Enum

def random_maze():
	maze_idx = random.randint(0, len(mazes) - 1)
	return Maze(mazes[maze_idx])

def maze(idx):
	return Maze(mazes[idx])

class Direction(Enum):
	LEFT = 1
	RIGHT = 2
	UP = 3
	DOWN = 4

class Maze:
	image_size = 64
	margin = 16
	start_flag = 2
	finish_flag = 4
	base_textures = [
		'plf:Ground_GrassCenter',
		'plf:Ground_StoneCenter'
	]
	special_textures = dict([
		(2, 'plf:HudPlayer_yellow'),
		(4, 'plf:Item_CoinGold')
	])
	default_speed = 24
	
	def __init__(self, flags):
		self.flags = flags
		self.speed = Maze.default_speed
		self.player = None
		self.player_idx = None
		self.player_go_idx = None
		self.player_step_count = None
		self.coordinates = None
		self.start_idx = None
		self.finish_idx = None
	
	def num_of_rows(self):
		return len(self.flags)
	
	def num_of_columns(self):
		return len(self.flags[0]) if len(self.flags) > 0 else 0
	
	def can_player_go(self, direction: Direction):
		match direction:
			case Direction.LEFT:
				return self.player_idx[1] - 1 >= 0 and self.flags[self.player_idx[0]][self.player_idx[1] - 1] % 2 == 0
			case Direction.RIGHT:
				return self.player_idx[1] + 1 < self.num_of_columns() and self.flags[self.player_idx[0]][self.player_idx[1] + 1] % 2 == 0
			case Direction.UP:
				return self.player_idx[0] - 1 >= 0 and self.flags[self.player_idx[0] - 1][self.player_idx[1]] % 2 == 0
			case Direction.DOWN:
				return self.player_idx[0] + 1 < self.num_of_rows() and self.flags[self.player_idx[0] + 1][self.player_idx[1]] % 2 == 0
		return False
	
	def player_go(self, direction: Direction):
		if not self.can_player_go(direction):
			return
		self.player_step_count = 0
		match direction:
			case Direction.LEFT:
				self.player_go_idx = (self.player_idx[0], self.player_idx[1] - 1)
			case Direction.RIGHT:
				self.player_go_idx = (self.player_idx[0], self.player_idx[1] + 1)
			case Direction.UP:
				self.player_go_idx = (self.player_idx[0] - 1, self.player_idx[1])
			case Direction.DOWN:
				self.player_go_idx = (self.player_idx[0] + 1, self.player_idx[1])
	
	def player_move(self):
		if self.player_go_idx == None:
			return False
		self.player_step_count = self.player_step_count + 1
		if self.player_step_count < self.speed:
			x = self.coordinates[self.player_idx[0]][self.player_idx[1]][0] + ((self.player_go_idx[1] - self.player_idx[1]) * (self.player_step_count / self.speed * Maze.image_size * self.scale))
			y = self.coordinates[self.player_idx[0]][self.player_idx[1]][1] + ((self.player_idx[0] - self.player_go_idx[0]) * (self.player_step_count / self.speed * Maze.image_size * self.scale))
			self.player.position = (x, y)
		else:
			self.player_idx = self.player_go_idx
			self.player_go_idx = None
			self.player_step_count = 0
			self.player.position = self.coordinates[self.player_idx[0]][self.player_idx[1]]
		return True
	
	def finished(self):
		return self.player_idx == self.finish_idx
	
	def set_speed(self, speed):
		self.speed = speed
	
	def setup(self, scene: Scene):
		self.scale = self.__calculate_scale(scene)
		self.__setup_maze(scene, self.scale)	
		
	def __setup_maze(self, scene, scale):
		self.coordinates = [None] * self.num_of_rows()
		corner = self.__calculate_corner(scene, scale)
		original_x = corner[0]
		x = corner[0]
		y = corner[1]
		for i in range(self.num_of_rows() - 1, -1, -1):
			self.coordinates[i] = [None] * self.num_of_columns()
			for j in range(self.num_of_columns()):
				flag = self.flags[i][j]
				if flag == Maze.start_flag:
					self.start_idx = (i, j)
					self.player_idx = (i, j)
				elif flag == Maze.finish_flag:
					self.finish_idx = (i, j)
				self.__add_base_tile(scene, scale, flag, x, y)
				self.__add_special_element(scene, scale, flag, x, y)
				self.coordinates[i][j] = (x, y)
				x = x + (scale * Maze.image_size)
			x = original_x
			y = y + (scale * Maze.image_size)
		scene.add_child(self.player)
	
	def __add_base_tile(self, scene, scale, flag, x, y):
		texture = Maze.base_textures[flag % 2]
		tile = SpriteNode(texture)
		tile.anchor_point = (0, 0)
		tile.position = (x, y)
		tile.scale = scale
		scene.add_child(tile)
	
	def __add_special_element(self, scene, scale, flag, x, y):
		if flag in Maze.special_textures:
			texture = Maze.special_textures[flag]
			special_element = SpriteNode(texture)
			special_element.anchor_point = (0, 0)
			special_element.position = (x, y)
			special_element.scale = scale
			#add player as last child so it'll be on top
			if flag == Maze.start_flag:
				self.player = special_element
			else:
				scene.add_child(special_element)
	
	def __calculate_scale(self, scene):
		max_image_width = (Maze.image_size * self.num_of_columns()) + (2 * Maze.margin)
		max_image_height = (Maze.image_size * self.num_of_rows()) + (2 * Maze.margin)
		scale = min(scene.size.w / max_image_width, scene.size.h / max_image_height)
		return 1.0 if scale > 1.0 else round(scale, 1)
	
	def __calculate_corner(self, scene, scale):
		x = (scene.size.w / 2) - (self.num_of_columns() / 2 * Maze.image_size * scale)
		y = (scene.size.h / 2) - (self.num_of_rows() / 2 * Maze.image_size * scale)
		return (x, y)

mazes = [
	[
		[1, 1, 1, 1, 1, 1, 1, 1, 1],
		[1, 0, 0, 0, 0, 0, 1, 0, 4],
		[1, 1, 1, 1, 1, 0, 0, 0, 1],
		[1, 0, 1, 0, 1, 0, 1, 1, 1],
		[1, 0, 0, 0, 1, 0, 0, 0, 1],
		[1, 0, 1, 0, 1, 0, 1, 0, 1],
		[1, 0, 1, 1, 1, 1, 1, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 1, 1, 1, 0, 1, 0, 1],
		[1, 0, 0, 0, 0, 0, 1, 0, 1],
		[1, 1, 2, 1, 1, 1, 1, 1, 1]
	],
	[
		[1, 1, 1, 1, 1, 1, 1, 4, 1],
		[1, 0, 0, 0, 0, 0, 1, 0, 1],
		[1, 0, 1, 1, 1, 0, 0, 0, 1],
		[1, 0, 1, 0, 1, 0, 1, 1, 1],
		[1, 0, 0, 0, 1, 0, 0, 0, 1],
		[1, 0, 1, 0, 0, 0, 1, 0, 1],
		[1, 1, 1, 1, 1, 1, 1, 0, 1],
		[1, 0, 0, 0, 0, 0, 0, 0, 1],
		[1, 0, 1, 1, 1, 0, 1, 0, 1],
		[1, 0, 0, 0, 0, 0, 1, 0, 1],
		[1, 1, 2, 1, 1, 1, 1, 1, 1]
	],
	[
		[1, 1, 2, 1, 1, 1, 1],
		[1, 0, 0, 0, 0, 0, 1],
		[1, 0, 1, 0, 1, 0, 1],
		[1, 0, 0, 0, 0, 0, 1],
		[1, 0, 1, 1, 1, 0, 1],
		[1, 0, 1, 0, 0, 0, 1],
		[1, 0, 0, 0, 1, 0, 1],
		[1, 0, 1, 0, 1, 0, 1],
		[1, 0, 1, 0, 0, 0, 1],
		[1, 1, 1, 4, 1, 1, 1]
	],
	[
		[1, 1, 1, 1, 1, 1],
		[1, 0, 0, 0, 1, 1],
		[1, 0, 1, 0, 1, 1],
		[1, 0, 0, 0, 0, 4],
		[1, 1, 1, 2, 1, 1]
	]
]
