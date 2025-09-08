import unittest
from unittest.mock import MagicMock
import logging
import sys
sys.modules['ui'] = MagicMock()

from cube_view import Cube

class CubeTestCase(unittest.TestCase):
    def test_default_model_state(self):
        cube = Cube()
        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;RRRRRRRRR;FFFFFFFFF;DDDDDDDDD;LLLLLLLLL;BBBBBBBBB')

    def test_model_after_U(self):
        cube = Cube()
        moves = ['U']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;BBBRRRRRR;RRRFFFFFF;DDDDDDDDD;FFFLLLLLL;LLLBBBBBB')

    def test_model_after_U_(self):
        cube = Cube()
        moves = ['U\'']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;FFFRRRRRR;LLLFFFFFF;DDDDDDDDD;BBBLLLLLL;RRRBBBBBB')

    def test_model_after_D(self):
        cube = Cube()
        moves = ['D']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;RRRRRRFFF;FFFFFFLLL;DDDDDDDDD;LLLLLLBBB;BBBBBBRRR')

    def test_model_after_D_(self):
        cube = Cube()
        moves = ['D\'']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUUUUU;RRRRRRBBB;FFFFFFRRR;DDDDDDDDD;LLLLLLFFF;BBBBBBLLL')

    def test_model_after_L(self):
        cube = Cube()
        moves = ['L']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUFUUFUUF;RRRRRRRRR;FFDFFDFFD;DDBDDBDDB;LLLLLLLLL;UBBUBBUBB')

    def test_model_after_L_(self):
        cube = Cube()
        moves = ['L\'']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUBUUBUUB;RRRRRRRRR;FFUFFUFFU;DDFDDFDDF;LLLLLLLLL;DBBDBBDBB')

    def test_model_after_R(self):
        cube = Cube()
        moves = ['R']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'BUUBUUBUU;RRRRRRRRR;UFFUFFUFF;FDDFDDFDD;LLLLLLLLL;BBDBBDBBD')

    def test_model_after_R_(self):
        cube = Cube()
        moves = ['R\'']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'FUUFUUFUU;RRRRRRRRR;DFFDFFDFF;BDDBDDBDD;LLLLLLLLL;BBUBBUBBU')

    def test_model_after_B(self):
        cube = Cube()
        moves = ['B']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'RRRUUUUUU;RRDRRDRRD;FFFFFFFFF;DDDDDDLLL;ULLULLULL;BBBBBBBBB')

    def test_model_after_B_(self):
        cube = Cube()
        moves = ['B\'']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'LLLUUUUUU;RRURRURRU;FFFFFFFFF;DDDDDDRRR;DLLDLLDLL;BBBBBBBBB')

    def test_model_after_F(self):
        cube = Cube()
        moves = ['F']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUULLL;URRURRURR;FFFFFFFFF;RRRDDDDDD;LLDLLDLLD;BBBBBBBBB')

    def test_model_after_F_(self):
        cube = Cube()
        moves = ['F\'']

        self.play_moves(cube, moves)

        self.assertEqual(cube.logic.as_string(),
            'UUUUUURRR;DRRDRRDRR;FFFFFFFFF;LLLDDDDDD;LLULLULLU;BBBBBBBBB')

    def play_moves(self, cube: 'Cube', moves):
        cube.play_moves(moves)
        current_move, _ = cube.update()
        while current_move is not None:
            current_move, _ = cube.update()
        

if __name__ == '__main__':
    unittest.main()
