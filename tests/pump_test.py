import unittest
import time

from pump import Pump

class TestPump(unittest.TestCase):
    def get_time(self):
        return self.emulated_time

    def setUp(self):
        # Define the emulated time
        self.emulated_time = time.mktime(
                time.strptime("2020-01-18 02:02:05", "%Y-%m-%d %H:%M:%S"))

        # Register the time.time function and patch it then
        self.time_method = time.time
        time.time = self.get_time

    def tearDown(self):
        # Restore the time.time function
        time.time = self.time_method

    def test_initial_values(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        self.assertEqual(pump.name, 'test_pump')
        self.assertEqual(pump.power, 200)
        self.assertEqual(pump.desired_runtime, 3 * 3600)
        self.assertIsNone(pump.on_since)

    def test_can_run_with_enough_power(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        self.assertTrue(pump.can_run(250))
        self.assertTrue(pump.can_run(200))
        self.assertFalse(pump.can_run(190))

    def test_should_run_until_desired(self):
        pump = Pump('test_pump', 200, 10)
        self.assertTrue(pump.should_run())
        pump.runtime = 10
        self.assertFalse(pump.should_run())

    def test_turn_on_stores_time(self):
        pump = Pump('test_pump', 200, 10)
        pump.turn_on()
        self.assertEqual(pump.on_since, self.emulated_time)

    def test_turn_off_updates_runtime(self):
        pump = Pump('test_pump', 200, 10)
        pump.turn_on()
        self.assertEqual(pump.on_since, self.emulated_time)
        self.emulated_time += 20
        pump.turn_off()
        self.assertIsNone(pump.on_since)
        self.assertEqual(pump.runtime, 20)