import time

class Pump:
    power = None
    name = None
    desired_runtime = 0
    runtime = 0
    on_since = None
    
    def __init__(self, name, power, runtime):
        self.power = power
        self.name = name
        self.desired_runtime = runtime
    
    def should_run(self):
        return self.runtime < self.desired_runtime
    
    def can_run(self, available_power):
        return available_power >= self.power
    
    def is_running(self):
        return self.on_since != None
    
    def turn_on(self):
        print(f'Starting pump {self.name}')
        # Call GPIO to turn the pump on
        self.on_since = time.time()
    
    def turn_off(self):
        ran_for = time.time() - self.on_since
        print(f'Stopping pump {self.name}, ran for {ran_for} seconds')
        # Call GPIO to turn the pump off
        self.runtime += ran_for
        self.on_since = None

    def update(self):
        if self.is_running():
            ran_for = time.time() - self.on_since
            if self.runtime + ran_for >= self.desired_runtime:
                self.turn_off()

        print(f'Pump {self.name} updated')