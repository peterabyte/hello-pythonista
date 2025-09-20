import unittest
from unittest.mock import MagicMock
import logging
import sys
sys.modules['ui'] = MagicMock()

from cube_view import Cube, play_moves, MOVE_MAP
from cube_model import CubeModel
from beginner_solver import BeginnerSolver

class CubeTestCase(unittest.TestCase):
    def test_default_model_state(self):
        cube = Cube()
        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;RRRRRRRRR;FFFFFFFFF;DDDDDDDDD;LLLLLLLLL;BBBBBBBBB')

    def test_model_after_U(self):
        cube = Cube()
        moves = ['U']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;BBBRRRRRR;RRRFFFFFF;DDDDDDDDD;FFFLLLLLL;LLLBBBBBB')

    def test_model_after_U_(self):
        cube = Cube()
        moves = ['U\'']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;FFFRRRRRR;LLLFFFFFF;DDDDDDDDD;BBBLLLLLL;RRRBBBBBB')

    def test_model_after_D(self):
        cube = Cube()
        moves = ['D']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;RRRRRRFFF;FFFFFFLLL;DDDDDDDDD;LLLLLLBBB;BBBBBBRRR')

    def test_model_after_D_(self):
        cube = Cube()
        moves = ['D\'']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;RRRRRRBBB;FFFFFFRRR;DDDDDDDDD;LLLLLLFFF;BBBBBBLLL')

    def test_model_after_L(self):
        cube = Cube()
        moves = ['L']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'BUUBUUBUU;RRRRRRRRR;UFFUFFUFF;FDDFDDFDD;LLLLLLLLL;BBDBBDBBD')

    def test_model_after_L_(self):
        cube = Cube()
        moves = ['L\'']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'FUUFUUFUU;RRRRRRRRR;DFFDFFDFF;BDDBDDBDD;LLLLLLLLL;BBUBBUBBU')

    def test_model_after_R(self):
        cube = Cube()
        moves = ['R']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUFUUFUUF;RRRRRRRRR;FFDFFDFFD;DDBDDBDDB;LLLLLLLLL;UBBUBBUBB')

    def test_model_after_R_(self):
        cube = Cube()
        moves = ['R\'']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUBUUBUUB;RRRRRRRRR;FFUFFUFFU;DDFDDFDDF;LLLLLLLLL;DBBDBBDBB')

    def test_model_after_B(self):
        cube = Cube()
        moves = ['B']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'RRRUUUUUU;RRDRRDRRD;FFFFFFFFF;DDDDDDLLL;ULLULLULL;BBBBBBBBB')

    def test_model_after_B_(self):
        cube = Cube()
        moves = ['B\'']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'LLLUUUUUU;RRURRURRU;FFFFFFFFF;DDDDDDRRR;DLLDLLDLL;BBBBBBBBB')

    def test_model_after_F(self):
        cube = Cube()
        moves = ['F']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUULLL;URRURRURR;FFFFFFFFF;RRRDDDDDD;LLDLLDLLD;BBBBBBBBB')

    def test_model_after_F_(self):
        cube = Cube()
        moves = ['F\'']

        play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUURRR;DRRDRRDRR;FFFFFFFFF;LLLDDDDDD;LLULLULLU;BBBBBBBBB')

    def test_cube_model_from_string_solved(self):
        cube_model = CubeModel.from_string('UUUUUUUUU;RRRRRRRRR;FFFFFFFFF;DDDDDDDDD;LLLLLLLLL;BBBBBBBBB')
        
        self.assertEqual(cube_model.as_string(), 'UUUUUUUUU;RRRRRRRRR;FFFFFFFFF;DDDDDDDDD;LLLLLLLLL;BBBBBBBBB')

    def test_cube_model_from_string_scrambled(self):
        cube_model = CubeModel.from_string('BUUBUUDUU;BBBURRURR;LRRLFFLFF;URRFDDFDD;LLFLLFDDF;LLDBBDBBR')
        
        self.assertEqual(cube_model.as_string(), 'BUUBUUDUU;BBBURRURR;LRRLFFLFF;URRFDDFDD;LLFLLFDDF;LLDBBDBBR')

    def test_solve_white_cross_when_already_solved(self):
        solver = BeginnerSolver()
        cube_model = CubeModel()
        
        solution = solver.solve_white_cross(cube_model)
        
        self.assertEqual(len(solution), 0)

    def test_move_map_U(self):
        move = 'U'
        total_deg = 90
        cube = Cube()
        
        axis, layer, _, _ = MOVE_MAP[move]
        result_move = cube.last_token_from_move(axis, layer, total_deg)
        
        self.assertEqual(result_move, move)

    def test_move_map_U_(self):
        move = "U'"
        total_deg = -90
        cube = Cube()
        
        axis, layer, _, _ = MOVE_MAP[move]
        result_move = cube.last_token_from_move(axis, layer, total_deg)
        
        self.assertEqual(result_move, move)

    def test_move_map_R(self):
        move = "R"
        total_deg = 90
        cube = Cube()
        
        axis, layer, _, _ = MOVE_MAP[move]
        result_move = cube.last_token_from_move(axis, layer, total_deg)
        
        self.assertEqual(result_move, move)

if __name__ == '__main__':
    unittest.main()
