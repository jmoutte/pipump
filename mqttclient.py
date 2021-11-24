import logging
import asyncio
import json

import paho.mqtt.client as mqtt

class MQTTClient():
    def __init__(self, options):
        self._host = options.get('host', '127.0.0.1')
        self._port = options.get('port', 1883)
        self._username = options.get('username', None)
        self._password = options.get('password', None)
        self._timeout = options.get('timeout', 60)
        self._uid = options.get('uid', '12345')
        self._discovery = options.get('discovery', True)
        self._discovery_prefix = options.get('discovery_prefix', 'homeassistant')
        self._pumps = []
        self._mode_changed_callback = None
        self._switch_callback = None

        self._client = mqtt.Client(client_id = f'pipump_{self._uid}', clean_session=True, userdata=None, protocol=4)
        if self._username:
            self._client.username_pw_set(self._username, password=self._password)
        self._client.on_connect = self.on_connected
    
    def attach(self, pumps, mode_callback, switch_callback):
        self._pumps = pumps
        for p in pumps:
            p.add_state_callback(self.on_pump_state_changed)
        self._mode_changed_callback = mode_callback
        self._switch_callback = switch_callback
    
    def on_pump_state_changed(self, pump, state):
        topic = f'{self._discovery_prefix}/switch/pipump_{self._uid}/{pump.name}/state'
        self._client.publish(topic, state, retain=True)
    
    def on_select_message(self, client, userdata, msg):
        new_mode = msg.payload.decode("utf-8")
        if self._mode_changed_callback:
            res = self._mode_changed_callback(new_mode)
            if res:
                topic = f'{self._discovery_prefix}/select/pipump_{self._uid}/state'
                client.publish(topic, new_mode, retain=True)

    def on_switch_message(self, client, userdata, msg):
        if self._switch_callback:
            payload = msg.payload.decode("utf-8")
            topic_parts = msg.topic.split('/')
            pump_name = topic_parts[len(topic_parts) - 2]
            for p in self._pumps:
                if p.name == pump_name:
                    self._switch_callback(p, payload)
                    break
    
    def announce_select(self):
        base_topic = f'{self._discovery_prefix}/select/pipump_{self._uid}'

        if self._discovery:
            device = {}
            device['identifiers'] = [ f'pipump.{self._uid}' ]
            device['manufacturer'] = 'Julien Moutte'
            device['model'] = 'PiPump Controller'
            device['name'] = 'Pump Controller'
            device['sw_version'] = '0.1'
            device['suggested_area'] = 'Swimming pool'
            
            payload = {}
            payload['name'] = 'Pump Controller'
            payload['unique_id'] = f'pipump.{self._uid}'
            payload['icon'] = 'mdi:table-clock'
            payload['entity_category'] = 'config'
            payload['command_topic'] = base_topic + '/set'
            payload['state_topic'] = base_topic + '/state'
            payload['options'] = ['AUTO', 'MANUAL', 'OFF']
            payload['device'] = device

            self._client.publish(f'{base_topic}/config', json.dumps(payload), retain=True)

        self._client.message_callback_add(f'{base_topic}/set', self.on_select_message)
        self._client.subscribe(f'{base_topic}/set')
        self._client.publish(f'{base_topic}/state', 'AUTO', retain=True)

    def announce_sensor(self, pump):
        base_topic = f'{self._discovery_prefix}/sensor/pipump_{self._uid}/{pump.name}'

        if self._discovery:
            device = {}
            device['identifiers'] = [ f'pipump.{self._uid}_{pump.name}' ]
            device['model'] = 'Water pump'
            device['name'] = 'Pump ' + pump.name
            device['suggested_area'] = 'Swimming pool'
            device['via_device'] = f'pipump.{self._uid}'

            payload = {}
            payload['name'] = 'Daily goal progress'
            payload['unique_id'] = f'pipump.{self._uid}_{pump.name}'
            payload['icon'] = 'mdi:progress-check'
            payload['entity_category'] = 'diagnostic'
            payload['unit_of_measurement'] = '%'
            payload['state_topic'] = base_topic + '/state'
            payload['device'] = device

            self._client.publish(f'{base_topic}/config', json.dumps(payload), retain=True)
        
        self._client.publish(f'{base_topic}/state', pump.goal_progress, retain=True)

    def announce_pump(self, pump):
        base_topic = f'{self._discovery_prefix}/switch/pipump_{self._uid}/{pump.name}'

        if self._discovery:
            device = {}
            device['identifiers'] = [ f'pipump.{self._uid}_{pump.name}' ]
            device['model'] = 'Water pump'
            device['name'] = 'Pump ' + pump.name
            device['suggested_area'] = 'Swimming pool'
            device['via_device'] = f'pipump.{self._uid}'

            payload = {}
            payload['name'] = 'Pump ' + pump.name
            payload['unique_id'] = f'pipump.{self._uid}_{pump.name}'
            payload['icon'] = 'mdi:engine'
            payload['entity_category'] = 'config'
            payload['command_topic'] = base_topic + '/set'
            payload['state_topic'] = base_topic + '/state'
            payload['device'] = device

            self._client.publish(f'{base_topic}/config', json.dumps(payload), retain=True)
        
        self._client.message_callback_add(f'{base_topic}/set', self.on_switch_message)
        self._client.subscribe(f'{base_topic}/set')
        self._client.publish(f'{base_topic}/state', 'ON' if pump.is_running() else 'OFF', retain=True)

    def on_connected(self, client, userdata, flags, rc):
        # Announce our select and one switch per pump
        if self._pumps:
            self.announce_select()
            for p in self._pumps:
                self.announce_pump(p)
                self.announce_sensor(p)

    async def task(self):
        self._client.connect(self._host, self._port, self._timeout)
        try:
            while True:
                self._client.loop(timeout=1, max_packets=1)
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logging.debug('mqtt_loop task cancelled')
            raise
