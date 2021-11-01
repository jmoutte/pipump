import unittest

from pvsystem import PVSystem

class TestPVSystem(unittest.TestCase):
    def test_initial_values(self):
        pvsystem = PVSystem()
        self.assertEqual(pvsystem.consumption, 0)
        self.assertEqual(pvsystem.production, 0)
