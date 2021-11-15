import os
import yaml
import logging

from pump import Pump
from envoy import Envoy
from mqttclient import MQTTClient

class Config():
    def __init__(self, filename):
        self._filename = filename
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), self._filename), 'r') as cfgfile:
            self._config = yaml.load(cfgfile, Loader=yaml.FullLoader)

    def load_pumps(self):
        pumps = []
        to_be_chained = []
        for cp in self._config['pumps']:
            p = Pump(cp['name'], cp['power'], cp['runtime'] * 3600, cp['gpio'])
            try:
                if cp['chained']:
                    to_be_chained.append((p, cp['chained']))
            except KeyError:
                pass
            pumps.append(p)
        for pump, target in to_be_chained:
            for p in pumps:
                if p.name == target:
                    pump.chain(p)
                    break
        return pumps
    
    def load_mqttclient(self):
        try:
            mqtt = self._config['mqtt']
            if mqtt:
                return MQTTClient(mqtt)
        except KeyError as err:
            logging.warning('missing attributes for mqttclient')
    
    def load_pvsystem(self):
        try:
            pvsystem = self._config['pvsystem']
            if pvsystem['type'] == 'envoy':
                return Envoy(pvsystem['ip'])
        except KeyError as err:
            logging.warning('missing attributes for pvsystem')
