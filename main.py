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
pumps = []
config = [ { 'name': 'Main', 'power': 1000, 'desired_runtime': 4 * 3600, 'GPIO_ID': 8 },
           { 'name': 'Polaris', 'power': 1000, 'desired_runtime': 1 * 3600, 'GPIO_ID': 10 } ]

for c in config:
    pumps.append(Pump(c['name'], c['power'], c['desired_runtime'], c['GPIO_ID']))

# FIXME
pumps[1].chain(pumps[0])

while True:
    for p in pumps:
        p.update()
    availability = device.update()
    for p in pumps:
        start = False
        if p.should_run():
            start, availability = p.can_run(availability)
        if start:
            p.turn_on()
        else:
            p.turn_off()
    sleep(60)
