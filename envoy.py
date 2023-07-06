import requests
import urllib3

from requests.exceptions import RequestException
from json import JSONDecodeError

from pvsystem import PVSystem
import logging

# We accept self signed certificates with no warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Envoy(PVSystem):
    def __init__(self, ip, user='', password='', serial=''):
        self._ip = ip
        self._user = user
        self._password = password
        self._serial = serial
        self._token = ''
        self._url = f'http://{ip}/production.json'
        PVSystem.__init__(self)
    
    @staticmethod
    def __get_eim_watts(data):
        for d in data:
            if d['type'] == 'eim':
                return d['wNow']
        return None
    
    def __refresh_token(self):
        data = {'user[email]': self._user, 'user[password]': self._password}
        resp = requests.post('https://enlighten.enphaseenergy.com/login/login.json?', data=data)
        if (resp.status_code != 200):
            logging.error(f'failed authenticating with enlighten for user {self._user}')
            raise ConnectionRefusedError()
        session_data = resp.json()
        session_id = session_data['session_id']
        if (not session_id):
            logging.error(f'no session_id provided after authentication')
            raise ConnectionRefusedError
        logging.debug(f'obtained session with id {session_id} for user {self._user}')
        data = {'session_id': session_id, 'serial_num': self._serial, 'username': self._user}
        resp = requests.post('https://entrez.enphaseenergy.com/tokens', json=data)
        if (resp.status_code != 200 or not resp.text):
            logging.error(f'failed getting token for user {self._user} and serial {self._serial}')
            raise ConnectionRefusedError()
        self._token = resp.text
        logging.debug(f'successfully renewed token for user {self._user}')

    def update(self):
        try:
            resp = None
            if (self._token):
                resp = requests.get(self._url, verify=False, headers={'Authorization': f'Bearer {self._token}'}, timeout=10)
            else:
                resp = requests.get(self._url, verify=False, timeout=10)

            # we either have no token or the previous one expired
            if (resp.status_code == 401):
                logging.debug(f'authentication failed when calling Envoy API')
                self.__refresh_token()
                # Try again
                resp = requests.get(self._url, verify=False, headers={'Authorization': f'Bearer {self._token}'}, timeout=10)
            elif (resp.status_code != 200):
                logging.debug(f'received unexpected HTTP status code {resp.status_code} when querying Envoy API')
                return 0
            
            data = resp.json()
            consumption = self.__get_eim_watts(data['consumption'])
            production = self.__get_eim_watts(data['production'])
            logging.debug(f'new reading: Production: {production}wH, Consumption: {consumption}wH')
            # Update moving average in base class
            self.consumption = consumption
            self.production = production
            logging.debug(f'moving average: Production: {self.production}wH, Consumption: {self.consumption}wH')
        except ConnectionRefusedError as e:
            logging.error(f'failed authenticating with Envoy device {self._ip}')
        except JSONDecodeError as e:
            logging.error(f'failed decoding JSON document from Envoy production API')
        except RequestException as e:
            logging.error(f'GET request on {self._url} triggered an exception {e.__class__.__name__}')
        # Return the latest value even in case of timeouts
        return self.production - self.consumption