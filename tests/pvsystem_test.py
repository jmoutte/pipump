import unittest

from pvsystem import PVSystem

class TestPVSystem(unittest.TestCase):
    def test_initial_values(self):
        pvsystem = PVSystem()
        self.assertEqual(pvsystem.consumption, None)
        self.assertEqual(pvsystem.production, None)
