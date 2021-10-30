class Pump:
    power = None
    name = None
    desired_runtime = 0
    runtime = 0
    
    def __init__(self, name, power, runtime):
        self.power = power
        self.name = name
        self.desired_runtime = runtime
    
    def should_run(self):
        return self.runtime < self.desired_runtime
    
    def can_run(self, available_power):
        return available_power >= self.power
    
    def turn_on(self):
        print(f'Starting pump {self.name}')

    def update(self):
        # Check if the pump is currently running

        # If it does, since when

        # Cumulate with current runtime

        # Do we need to stop it ?
        print(f'Pump {self.name} updated')