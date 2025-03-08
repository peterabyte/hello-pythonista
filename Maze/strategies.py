from mazes import Maze, Direction
import random

def left_hand(maze: Maze):
	return LeftHandOnWall(maze)

def right_hand(maze: Maze):
	return RightHandOnWall(maze)
	
def random_mouse(maze: Maze):
	return RandomMouse(maze)

class LeftHandOnWall:
	orientation = {
		Direction.LEFT: [Direction.DOWN, Direction.LEFT, Direction.UP, Direction.RIGHT],
		Direction.UP: [Direction.LEFT, Direction.UP, Direction.RIGHT, Direction.DOWN],
		Direction.RIGHT: [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT],
		Direction.DOWN: [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
	}
	
	def __init__(self, maze: Maze):
		self.maze = maze
		self.directions = [Direction.LEFT, Direction.UP, Direction.RIGHT, Direction.DOWN]
	
	def where_to_go(self):
		for direction in list(self.directions):
			if self.maze.can_player_go(direction):
				self.directions = LeftHandOnWall.orientation[direction]
				return direction
		return None

class RightHandOnWall:
	orientation = {
		Direction.RIGHT: [Direction.DOWN, Direction.RIGHT, Direction.UP, Direction.LEFT],
		Direction.UP: [Direction.RIGHT, Direction.UP, Direction.LEFT, Direction.DOWN],
		Direction.LEFT: [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT],
		Direction.DOWN: [Direction.LEFT, Direction.DOWN, Direction.RIGHT, Direction.UP]
	}
	
	def __init__(self, maze: Maze):
		self.maze = maze
		self.directions = [Direction.RIGHT, Direction.UP, Direction.LEFT, Direction.DOWN]
	
	def where_to_go(self):
		for direction in list(self.directions):
			if self.maze.can_player_go(direction):
				self.directions = RightHandOnWall.orientation[direction]
				return direction
		return None

class RandomMouse:
	oposites = {
		Direction.LEFT: Direction.RIGHT,
		Direction.RIGHT: Direction.LEFT,
		Direction.UP: Direction.DOWN,
		Direction.DOWN: Direction.UP
	}
	
	def __init__(self, maze: Maze):
		self.maze = maze
		self.direction = None
	
	def where_to_go(self):
		possible_directions = []
		for direction in list(RandomMouse.oposites):
			if self.maze.can_player_go(direction):
				possible_directions.append(direction)
		if len(possible_directions) == 1:
			self.direction = possible_directions[0]
			return self.direction
		elif len(possible_directions) > 1:
			if self.direction != None and RandomMouse.oposites[self.direction] in possible_directions:
				possible_directions.remove(RandomMouse.oposites[self.direction])
			self.direction = possible_directions[random.randint(0, len(possible_directions) - 1)]
			return self.direction
		return None
	
