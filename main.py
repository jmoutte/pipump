from envoy import Envoy
from pump import Pump
from time import sleep

device = Envoy('192.168.10.12')
# 1kWh, 4 hours per day
pump1 = Pump('Main', 1000, 4 * 3600)
# 1kWh, 1 hour per day
pump2 = Pump('Polaris', 1000, 1 * 3600)

while True:
    pump1.update()
    pump2.update()
    if pump1.should_run():
        device.update()
        print(f'Production: {device.production}wH')
        print(f'Consumption: {device.consumption}wH')
        if pump1.can_run(device.production - device.consumption):
            pump1.turn_on()
            if pump2.should_run and pump2.can_run(device.production - device.consumption):
                pump2.turn_on()
    sleep(60)