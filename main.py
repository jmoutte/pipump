from unittest.main import main
from envoy import Envoy
from pump import Pump

from time import sleep
import signal
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

emulate_pi = False
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
except ImportError:
    emulate_pi = True

def signal_handler(sig, frame):
    logging.info('Exiting cleanly')
    if not emulate_pi:
        GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

device = Envoy('192.168.10.12')

main_pump = Pump('Main', 1650, 3 * 3600, 8)
aux_pump = Pump('Polaris', 1100, 0.5 * 3600, 10)

aux_pump.chain(main_pump)

pumps = [main_pump, aux_pump]

while True:
    for p in pumps:
        p.update() # Potentially stops a pump that reached desired runtime, update counters
    availability = device.update()
    if availability <= 0:
        if aux_pump.is_running():
            aux_pump.turn_off()
            del device.consumption
        elif main_pump.is_running():
            main_pump.turn_off()
            del device.consumption
    else:
        for p in pumps:
            start = False
            if p.should_run():
                start, availability = p.can_run(availability)
            if start and not p.is_running():
                p.turn_on()
                del device.consumption
    sleep(60)
