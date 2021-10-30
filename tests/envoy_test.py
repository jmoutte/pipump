import unittest

from envoy import Envoy

class TestEnvoy(unittest.TestCase):
    def test_url(self):
        envoy = Envoy('127.0.0.1')
        self.assertEqual(envoy.ip, '127.0.0.1')
        self.assertEqual(envoy.url, 'http://127.0.0.1/production.json')
