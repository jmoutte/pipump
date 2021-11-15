import unittest
from unittest.mock import Mock
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
        self.assertEqual(pump.runtime, 0)
        self.assertEqual(pump.desired_runtime, 3 * 3600)
        self.assertIsNone(pump.on_since)
        self.assertIsNone(pump.chained_to)
        self.assertIsNone(pump.GPIO_ID)
    
    def test_initial_values_with_GPIO(self):
        pump = Pump('test_pump', 200, 3 * 3600, 15)
        self.assertEqual(pump.GPIO_ID, 15)

    def test_can_run_with_enough_power_when_off(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        self.assertEqual(pump.can_run(250), (True, 50))
        self.assertEqual(pump.can_run(200), (True, 0))
        self.assertEqual(pump.can_run(190), (False, 190))

    def test_can_run_with_enough_power_when_on(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        pump.turn_on()
        self.assertEqual(pump.can_run(250), (True, 250))
        self.assertEqual(pump.can_run(50), (True, 50))
        self.assertEqual(pump.can_run(-20), (False, -20))

    def test_should_run_until_desired_runtime(self):
        pump = Pump('test_pump', 200, 10)
        self.assertTrue(pump.should_run())
        pump.runtime = 10
        self.assertFalse(pump.should_run())
        pump.runtime = 100
        self.assertFalse(pump.should_run())

    def test_turn_on_stores_time(self):
        pump = Pump('test_pump', 200, 10)
        pump.turn_on()
        self.assertEqual(pump.on_since, self.emulated_time)
    
    def test_turn_on_when_running(self):
        pump = Pump('test_pump', 200, 10)
        pump.turn_on()
        self.assertEqual(pump.on_since, self.emulated_time)
        self.emulated_time += 20
        pump.turn_on()
        self.assertNotEqual(pump.on_since, self.emulated_time)

    def test_turn_off_updates_runtime(self):
        pump = Pump('test_pump', 200, 10)
        pump.turn_on()
        self.assertEqual(pump.on_since, self.emulated_time)
        self.emulated_time += 20
        pump.turn_off()
        self.assertIsNone(pump.on_since)
        self.assertEqual(pump.runtime, 20)
    
    def test_turn_off_when_off(self):
        pump = Pump('test_pump', 200, 10)
        pump.turn_off()
        self.assertIsNone(pump.on_since)
        self.assertEqual(pump.runtime, 0)
    
    def test_update_turns_off_at_desired_runtime(self):
        pump = Pump('test_pump', 200, 10)
        pump.turn_on()
        self.emulated_time += 10
        pump.update()
        self.assertEqual(pump.runtime, 10)
        self.assertFalse(pump.is_running())
    
    def test_update_resets_runtime_at_date_change(self):
        pump = Pump('test_pump', 200, 10)
        pump.runtime = 5
        self.emulated_time += 24 * 3600
        pump.update()
        self.assertEqual(pump.runtime, 0)
    
    def test_update_turns_off_at_date_change(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        self.emulated_time = time.mktime(
                time.strptime("2020-01-18 23:30:00", "%Y-%m-%d %H:%M:%S"))
        pump.turn_on()
        self.emulated_time += 1 * 3600
        pump.update()
        self.assertEqual(pump.runtime, 0)
        self.assertFalse(pump.is_running())

    def test_add_state_callback(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        callback = Mock()
        pump.add_state_callback(callback)
        pump.turn_on()
        callback.assert_called_once_with(pump, 'ON')
        callback.reset_mock()
        pump.turn_off()
        callback.assert_called_once_with(pump, 'OFF')
    
    def test_add_state_callbacks(self):
        pump = Pump('test_pump', 200, 3 * 3600)
        callback1 = Mock()
        callback2 = Mock()
        pump.add_state_callback(callback1)
        pump.add_state_callback(callback2)
        pump.turn_on()
        callback1.assert_called_once_with(pump, 'ON')
        callback2.assert_called_once_with(pump, 'ON')
        callback1.reset_mock()
        callback2.reset_mock()
        pump.turn_off()
        callback1.assert_called_once_with(pump, 'OFF')
        callback2.assert_called_once_with(pump, 'OFF')

class TestPumpChain(unittest.TestCase):
    def test_chain(self):
        pump1 = Pump('main_pump', 200, 3 * 3600)
        pump2 = Pump('aux_pump', 200, 1 * 3600)
        pump2.chain(pump1)
        self.assertEqual(pump2.chained_to, pump1)

    def test_is_chained(self):
        pump1 = Pump('main_pump', 200, 3 * 3600)
        pump2 = Pump('aux_pump', 200, 1 * 3600)
        pump2.chain(pump1)
        self.assertTrue(pump2.is_chained())
    
    def test_should_run(self):
        pump1 = Pump('main_pump', 200, 3 * 3600)
        pump2 = Pump('aux_pump', 200, 1 * 3600)
        pump2.chain(pump1)
        self.assertTrue(pump1.should_run())
        self.assertTrue(pump2.should_run())
        pump1.runtime = 3 * 3600
        self.assertFalse(pump1.should_run())
        self.assertFalse(pump2.should_run())

    def test_can_not_run_alone(self):
        pump1 = Pump('main_pump', 200, 3 * 3600)
        pump2 = Pump('aux_pump', 200, 1 * 3600)
        pump2.chain(pump1)
        self.assertEqual(pump1.can_run(1000), (True, 800))
        self.assertEqual(pump2.can_run(800), (False, 800))
        pump1.turn_on()
        self.assertEqual(pump1.can_run(1000), (True, 1000))
        self.assertEqual(pump2.can_run(1000), (True, 800))
    
    def test_can_run_with_enough_power_when_off(self):
        pump1 = Pump('main_pump', 200, 3 * 3600)
        pump2 = Pump('aux_pump', 200, 1 * 3600)
        pump2.chain(pump1)
        pump1.turn_on()
        self.assertEqual(pump1.can_run(100), (True, 100))
        self.assertEqual(pump2.can_run(100), (False, 100))
        self.assertEqual(pump2.can_run(250), (True, 50))
    
    def test_can_run_with_enough_power_when_on(self):
        pump1 = Pump('main_pump', 200, 3 * 3600)
        pump2 = Pump('aux_pump', 200, 1 * 3600)
        pump2.chain(pump1)
        pump1.turn_on()
        pump2.turn_on()
        self.assertEqual(pump1.can_run(100), (True, 100))
        self.assertEqual(pump2.can_run(100), (True, 100))

    def test_can_run_main_before_aux(self):
        pump1 = Pump('main_pump', 200, 3 * 3600)
        pump2 = Pump('aux_pump', 200, 1 * 3600)
        pump2.chain(pump1)
        start, availability = pump1.can_run(400)
        self.assertTrue(start)
        self.assertEqual(availability, 200)
        pump1.turn_on()
        start, availability = pump2.can_run(availability)
        self.assertTrue(start)
        self.assertEqual(availability, 0)

    def test_can_run_main_before_aux_not_enough_power(self):
        pump1 = Pump('main_pump', 200, 3 * 3600)
        pump2 = Pump('aux_pump', 200, 1 * 3600)
        pump2.chain(pump1)
        start, availability = pump1.can_run(300)
        self.assertTrue(start)
        self.assertEqual(availability, 100)
        pump1.turn_on()
        start, availability = pump2.can_run(availability)
        self.assertFalse(start)
        self.assertEqual(availability, 100)
