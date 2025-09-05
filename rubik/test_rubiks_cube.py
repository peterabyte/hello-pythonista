import unittest
from unittest.mock import MagicMock

import sys
sys.modules['ui'] = MagicMock()

from cube_view import Cube

class CubeTestCase(unittest.TestCase):
    def test(self):
        cube = Cube()
        self.maxDiff = None
        self.assertEqual(cube.state(), {})
