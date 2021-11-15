import requests
from requests.exceptions import RequestException
from pvsystem import PVSystem
import logging

class Envoy(PVSystem):
    def __init__(self, ip):
        self._ip = ip
        self._url = f'http://{ip}/production.json'
        PVSystem.__init__(self)
    
    @staticmethod
    def __get_eim_watts(data):
        for d in data:
            if d['type'] == 'eim':
                return d['wNow']
        return None

    def update(self):
        try:
            resp = requests.get(self._url, timeout=10)
            data = resp.json()
            consumption = self.__get_eim_watts(data['consumption'])
            production = self.__get_eim_watts(data['production'])
            logging.debug(f'new reading: Production: {production}wH, Consumption: {consumption}wH')
            # Update moving average in base class
            self.consumption = consumption
            self.production = production
            logging.debug(f'moving average: Production: {self.production}wH, Consumption: {self.consumption}wH')
        except RequestException as e:
            logging.error(f'GET request on {self._url} triggered an exception {e.__class__.__name__}')
        # Return the latest value even in case of timeouts
        return self.production - self.consumption