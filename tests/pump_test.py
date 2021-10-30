import unittest

from pump import Pump

class TestPump(unittest.TestCase):
    def test_initial_values(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        self.assertEqual(pump.name, 'test_pump')
        self.assertEqual(pump.power, 200)
        self.assertEqual(pump.desired_runtime, 3 * 3600)

    def test_can_run_with_enough_power(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        self.assertTrue(pump.can_run(250))
        self.assertTrue(pump.can_run(200))
        self.assertFalse(pump.can_run(190))

    def test_should_run_until_desired(self):
        pump = Pump('test_pump', 200, 10)
        self.assertTrue(pump.should_run())