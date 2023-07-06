from config import Config

import signal
import sys
import os
import logging
import asyncio

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'debug.log'))
    ]
)

mode = 'AUTO'
auto_task = None
emulate_pi = False
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
except ImportError:
    emulate_pi = True

def signal_handler(sig, frame):
    logging.info('Exiting cleanly')
    loop.stop()
    if not emulate_pi:
        GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def on_mode_changed(new_mode):
    global auto_task,mode

    if mode == new_mode:
        return mode

    logging.info(f'changing operation mode from {mode} to {new_mode}')

    if mode == 'AUTO':
        if auto_task is not None:
            auto_task.cancel()

    if new_mode == 'AUTO':
        auto_task = loop.create_task(auto_loop())
    else:
        for p in pumps:
            p.turn_off()

    mode = new_mode

    return mode

def on_switch_command(pump, command):
    if mode != 'MANUAL':
        logging.debug('ignoring switch command in non MANUAL modes')
        return
    else:
        if command == 'ON':
            pump.turn_on()
        elif command == 'OFF':
            pump.turn_off()
        else:
            logging.warning(f'Invalid command {command} for pump {pump.name}')

async def auto_loop():
    try:
        while True:
            for p in pumps:
                p.update() # Potentially stops a pump that reached desired runtime, update counters
            availability = device.update()
            if availability <= 0:
                if aux_pump and aux_pump.is_running():
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
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        logging.debug('auto_loop task cancelled')
        raise

config = Config('config.yaml')
pumps = config.load_pumps()
device = config.load_pvsystem()
mqtt_client = config.load_mqttclient()
if mqtt_client:
    mqtt_client.attach(pumps, on_mode_changed, on_switch_command)

# FIXME: need to find a better way to implement that logic
main_pump = None
aux_pump = None
for p in pumps:
    if p.is_chained():
        aux_pump = p
    else:
        main_pump = p

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    if mode == 'AUTO':
        auto_task = loop.create_task(auto_loop())

    if mqtt_client:
        mqtt_task = loop.create_task(mqtt_client.task())

    loop.run_forever()
    loop.close()
