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
    GPIO_ID = None
    current_date = None
    
    def __init__(self, name, power, runtime, GPIO_ID = None):
        self.power = power
        self.name = name
        self.desired_runtime = runtime
        self.GPIO_ID = GPIO_ID
        self.current_date = datetime.today().date()

        if self.GPIO_ID and not emulate_pi:
            logging.debug(f'Setting up GPIO {self.GPIO_ID} for pump {self.name}')
            GPIO.setup(self.GPIO_ID, GPIO.OUT, initial=GPIO.HIGH)
    
    def should_run(self):
        if self.chained_to and not self.chained_to.should_run():
            return False
        return self.runtime < self.desired_runtime
    
    def can_run(self, available_power):
        if self.chained_to:
            availability = available_power - self.power
            if self.is_running():
                availability = available_power
            start, availability = self.chained_to.can_run(availability)
            if start:
                return True, available_power - self.power
            else:
                return False, available_power
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
    
    def turn_on(self):
        if not self.is_running():
            logging.info(f'Starting pump {self.name}')
            # Call GPIO to turn the pump on
            if self.GPIO_ID and not emulate_pi:
                logging.debug(f'Setting GPIO {self.GPIO_ID} to LOW for pump {self.name}')
                GPIO.output(self.GPIO_ID, GPIO.LOW)
            self.on_since = time.time()
    
    def turn_off(self):
        if self.is_running():
            ran_for = time.time() - self.on_since
            logging.info(f'Stopping pump {self.name}, ran for {ran_for} seconds, day runtime {self.runtime} seconds')
            # Call GPIO to turn the pump off
            if self.GPIO_ID and not emulate_pi:
                logging.debug(f'Setting GPIO {self.GPIO_ID} to HIGH for pump {self.name}')
                GPIO.output(self.GPIO_ID, GPIO.HIGH)
            self.runtime += ran_for
            self.on_since = None

    def update(self):
        if self.is_running():
            ran_for = time.time() - self.on_since
            if self.runtime + ran_for >= self.desired_runtime:
                self.turn_off()
        
        now = datetime.today().date()
        if self.current_date != now:
            # Reset counters
            self.runtime = 0
            self.current_date = now

        logging.debug(f'Pump {self.name} updated, day runtime {self.runtime}, desired {self.desired_runtime}, running {self.is_running()}')
