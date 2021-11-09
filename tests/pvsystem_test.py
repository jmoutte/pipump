import unittest

from pvsystem import PVSystem

class TestPVSystem(unittest.TestCase):
    def test_initial_values(self):
        pvsystem = PVSystem()
        self.assertEqual(pvsystem.consumption, 0)
        self.assertEqual(pvsystem.production, 0)

    def test_set_values_first(self):
        pvsystem = PVSystem()
        pvsystem.production = 100
        pvsystem.consumption = 100
        self.assertEqual(pvsystem.consumption, 100)
        self.assertEqual(pvsystem.production, 100)

    def test_set_values_moving_average(self):
        pvsystem = PVSystem()
        for c in [0, 100, 200, 100, 0]:
            pvsystem.consumption = c
        for p in [50, 60, 80, 100, 110]:
            pvsystem.production = p
        self.assertEqual(pvsystem.consumption, 80)
        self.assertEqual(pvsystem.production, 80)

    def test_del_clears_moving_average(self):
        pvsystem = PVSystem()
        for i in [0, 100, 200, 100, 0]:
            pvsystem.consumption = i
            pvsystem.production = i
        self.assertEqual(pvsystem.consumption, 80)
        self.assertEqual(pvsystem.production, 80)
        del pvsystem.production
        del pvsystem.consumption
        self.assertEqual(pvsystem.consumption, 0)
        self.assertEqual(pvsystem.production, 0)
