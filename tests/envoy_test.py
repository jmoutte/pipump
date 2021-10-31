import unittest
from unittest.mock import patch

from requests.exceptions import Timeout

from envoy import Envoy

class TestEnvoy(unittest.TestCase):
    def test_url(self):
        envoy = Envoy('127.0.0.1')
        self.assertEqual(envoy.ip, '127.0.0.1')
        self.assertEqual(envoy.url, 'http://127.0.0.1/production.json')
    
    def test_update_absorbs_timeout(self):
        envoy = Envoy('127.0.0.1')
        with patch('envoy.requests') as mock_requests:
            mock_requests.get.side_effect = Timeout
            envoy.update()
            mock_requests.get.assert_called_once_with('http://127.0.0.1/production.json')
