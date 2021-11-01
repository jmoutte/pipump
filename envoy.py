import requests
from requests.exceptions import RequestException
from pvsystem import PVSystem
import logging

class Envoy(PVSystem):
    ip = None
    url = None

    def __init__(self, ip):
        self.ip = ip
        self.url = f'http://{ip}/production.json'
        PVSystem.__init__(self)
    
    @staticmethod
    def __get_eim_watts(data):
        for d in data:
            if d['type'] == 'eim':
                return d['wNow']
        return None

    def update(self):
        try:
            resp = requests.get(self.url)
            data = resp.json()
            self.consumption = self.__get_eim_watts(data['consumption'])
            self.production = self.__get_eim_watts(data['production'])
            logging.debug(f'Production: {self.production}wH, Consumption: {self.consumption}wH')
        except RequestException as e:
            logging.error(f'GET request on {self.url} triggered an exception {e.strerror}')
        # Return the latest value even in case of timeouts
        return self.production - self.consumption