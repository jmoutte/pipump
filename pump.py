import time
import logging
from datetime import datetime

emulate_pi = False
try:
    import RPi.GPIO as GPIO
except ImportError:
    emulate_pi = True

class Pump:
    power = None
    name = None
    desired_runtime = 0
    runtime = 0
    on_since = None
    chained_to = None
    
    def __init__(self, name, power, runtime, GPIO_ID = None):
        self.power = power
        self.name = name
        self.desired_runtime = runtime
        self._GPIO_ID = GPIO_ID
        self._current_date = datetime.today().date()
        self._state_callbacks = []
        self._update_callbacks = []

        if self._GPIO_ID and not emulate_pi:
            logging.debug(f'setting up GPIO {self._GPIO_ID} for pump {self.name}')
            GPIO.setup(self._GPIO_ID, GPIO.OUT, initial=GPIO.HIGH)
    
    @property
    def goal_progress(self):
        runtime = self.runtime
        if self.on_since:
            runtime += time.time() - self.on_since
        return round(runtime * 100 / self.desired_runtime)

    def should_run(self):
        if self.chained_to and not self.chained_to.should_run():
            return False
        return self.runtime < self.desired_runtime
    
    def can_run(self, available_power):
        if self.chained_to:
            # We can only run when our upstream pump already runs
            if not self.chained_to.is_running():
                return False, available_power
            if self.is_running():
                return available_power >= 0, available_power
            else:
                start, availability = self.chained_to.can_run(available_power - self.power)
                if start:
                    return True, available_power - self.power
                else:
                    return False, available_power
        else:
            if self.is_running():
                return available_power >= 0, available_power
            if available_power >= self.power:
                return True, available_power - self.power
            else:
                return False, available_power
    
    def is_running(self):
        return self.on_since != None
    
    def chain(self, pump):
        self.chained_to = pump
    
    def is_chained(self):
        return self.chained_to != None
    
    def add_state_callback(self, callback):
        self._state_callbacks.append(callback)
    
    def add_update_callback(self, callback):
        self._update_callbacks.append(callback)
    
    def turn_on(self):
        if not self.is_running():
            logging.info(f'starting pump {self.name}')
            # Call GPIO to turn the pump on
            if self._GPIO_ID and not emulate_pi:
                logging.debug(f'setting GPIO {self._GPIO_ID} to LOW for pump {self.name}')
                GPIO.output(self._GPIO_ID, GPIO.LOW)
            self.on_since = time.time()
            for cb in self._state_callbacks:
                cb(self, 'ON')
    
    def turn_off(self):
        if self.is_running():
            ran_for = time.time() - self.on_since
            logging.info(f'stopping pump {self.name}, ran for {round(ran_for)} seconds, day runtime {round(self.runtime)} seconds')
            # Call GPIO to turn the pump off
            if self._GPIO_ID and not emulate_pi:
                logging.debug(f'setting GPIO {self._GPIO_ID} to HIGH for pump {self.name}')
                GPIO.output(self._GPIO_ID, GPIO.HIGH)
            self.runtime += ran_for
            self.on_since = None
            for cb in self._state_callbacks:
                cb(self, 'OFF')

    def update(self):
        notify = False
        if self.is_running():
            notify = True
            ran_for = time.time() - self.on_since
            if self.runtime + ran_for >= self.desired_runtime:
                self.turn_off()
        
        now = datetime.today().date()
        if self._current_date != now:
            notify = True
            logging.debug(f'date changed to next day for pump {self.name}, resetting counters and turning off if running')
            self.turn_off()
            # Reset counters
            self.runtime = 0
            self._current_date = now            

        if notify:
            progress = self.goal_progress
            for cb in self._update_callbacks:
                cb(self, progress)

        logging.debug(f'pump {self.name} updated, day runtime {round(self.runtime)}, desired {self.desired_runtime}, running {self.is_running()}')
