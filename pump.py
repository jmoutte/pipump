import time
import logging

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
    
    def __init__(self, name, power, runtime, GPIO_ID = None):
        self.power = power
        self.name = name
        self.desired_runtime = runtime
        self.GPIO_ID = GPIO_ID

        if self.GPIO_ID and not emulate_pi:
            logging.debug(f'Setting up GPIO {self.GPIO_ID} for pump {self.name}')
            GPIO.setup(self.GPIO_ID, GPIO.OUT)
    
    def should_run(self):
        if self.chained_to and not self.chained_to.should_run():
            return False
        return self.runtime < self.desired_runtime
    
    def can_run(self, available_power):
        if self.is_running():
            return available_power >= 0
        if self.chained_to:
            return self.chained_to.can_run(available_power - self.power)
        return available_power >= self.power
    
    def is_running(self):
        return self.on_since != None
    
    def chain(self, pump):
        self.chained_to = pump
    
    def turn_on(self):
        if not self.is_running():
            logging.info(f'Starting pump {self.name}')
            # Call GPIO to turn the pump on
            if self.GPIO_ID and not emulate_pi:
                logging.debug(f'Setting GPIO {self.GPIO_ID} to False for pump {self.name}')
                GPIO.output(self.GPIO_ID, False)
            self.on_since = time.time()
    
    def turn_off(self):
        if self.is_running():
            ran_for = time.time() - self.on_since
            logging.info(f'Stopping pump {self.name}, ran for {ran_for} seconds')
            # Call GPIO to turn the pump off
            if self.GPIO_ID and not emulate_pi:
                logging.debug(f'Setting GPIO {self.GPIO_ID} to True for pump {self.name}')
                GPIO.output(self.GPIO_ID, True)
            self.runtime += ran_for
            self.on_since = None

    def update(self):
        if self.is_running():
            ran_for = time.time() - self.on_since
            if self.runtime + ran_for >= self.desired_runtime:
                self.turn_off()

        logging.debug(f'Pump {self.name} updated')
