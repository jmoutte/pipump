import unittest

from pvsystem import PVSystem

class TestPVSystem(unittest.TestCase):
    def test_initial_values(self):
        pvsystem = PVSystem()
        self.assertEqual(pvsystem.consumption, 0)
        self.assertEqual(pvsystem.production, 0)

    def test_set_values_moving_average(self):
        pvsystem = PVSystem()
        for c in [0, 100, 200, 100, 0]:
            pvsystem.consumption = c
        for p in [50, 60, 80, 100, 110]:
            pvsystem.production = p
        self.assertEqual(pvsystem.consumption, 80)
        self.assertEqual(pvsystem.production, 80)
