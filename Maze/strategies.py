from mazes import Maze, Direction

def keep_left(maze: Maze):
	return KeepLeft(maze)

class KeepLeft:
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
				self.directions = KeepLeft.orientation[direction]
				return direction
		return None
