import requests
from requests.exceptions import RequestException
from pvsystem import PVSystem

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
        except RequestException as e:
            print(f'GET request on {self.url} triggered an exception {e.strerror}')