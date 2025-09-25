from abc import ABC, abstractmethod
from cube_model import CubeModel

class Solver(ABC):
    @abstractmethod
    def solve(self, cube: CubeModel) -> list:
        pass