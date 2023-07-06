import unittest
from unittest.mock import patch

from requests.exceptions import Timeout

from envoy import Envoy

class TestEnvoy(unittest.TestCase):
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[1] == 'http://127.0.0.1/production.json':
            return MockResponse({ "production": [{ "type": "eim", "wNow": 200 }], "consumption": [{ "type": "eim", "wNow": 100}] }, 200)

        return MockResponse(None, 404)
    
    def mocked_requests_get_with_auth(*args, **kwargs):
        class MockResponse:
            def __init__(self, status_code, json_data=None, headers={}):
                self.json_data = json_data
                self.status_code = status_code
                self.headers = headers
            def json(self):
                return self.json_data

        if args[1] == 'http://127.0.0.1/production.json':
            return MockResponse(status_code=301, headers={'Location': 'https://127.0.0.1/production.json'})
        elif args[1] == 'https://127.0.0.1/production.json':
            return MockResponse(status_code=200, json_data={ "production": [{ "type": "eim", "wNow": 200 }], "consumption": [{ "type": "eim", "wNow": 100}] })

        return MockResponse(None, 404)

    def test_url(self):
        envoy = Envoy('127.0.0.1')
        self.assertEqual(envoy._ip, '127.0.0.1')
        self.assertEqual(envoy._url, 'http://127.0.0.1/production.json')
    
    def test_update_absorbs_timeout(self):
        envoy = Envoy('127.0.0.1')
        with patch('envoy.requests') as mock_requests:
            mock_requests.get.side_effect = Timeout
            envoy.update()
            mock_requests.get.assert_called_once()
    
    def test_update_returns_availability(self):
        envoy = Envoy('127.0.0.1')
        with patch('envoy.requests') as mock_requests:
            mock_requests.get.side_effect = self.mocked_requests_get
            availability = envoy.update()
            self.assertEqual(availability, envoy.production - envoy.consumption)
