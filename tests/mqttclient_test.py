import unittest
from unittest.mock import Mock, patch

from mqttclient import MQTTClient

class TestMQTTClient(unittest.TestCase):
    def test_constructor_default_values(self):
        client = MQTTClient({})

        self.assertEqual(client._host, '127.0.0.1')
        self.assertEqual(client._port, 1883)
        self.assertEqual(client._username, None)
        self.assertEqual(client._password, None)
        self.assertEqual(client._timeout, 60)
        self.assertEqual(client._uid, '12345')
        self.assertTrue(client._discovery)
        self.assertEqual(client._discovery_prefix, 'homeassistant')
        self.assertEqual(client._pumps, [])
    
    def test_constructor_options(self):
        client = MQTTClient({ "host": "test.host.com", "port": 8080, "username": "john", "password": "doe", "timeout": 40, "uid": 'my_serial_num', "discovery": False, "discovery_prefix": "debug" })

        self.assertEqual(client._host, 'test.host.com')
        self.assertEqual(client._port, 8080)
        self.assertEqual(client._username, 'john')
        self.assertEqual(client._password, 'doe')
        self.assertEqual(client._timeout, 40)
        self.assertEqual(client._uid, 'my_serial_num')
        self.assertFalse(client._discovery)
        self.assertEqual(client._discovery_prefix, 'debug')
        self.assertEqual(client._pumps, [])

    def test_constructor_client_no_user(self):
        with patch('mqttclient.mqtt') as mock_client:
            client = MQTTClient({})
            mock_client.Client.assert_called_once_with(client_id = f'pipump_12345', clean_session = True, userdata = None, protocol = 4)
            mock_client.Client.username_pw_set.assert_not_called()

    def test_constructor_client_with_user(self):
        with patch('mqttclient.mqtt') as mock_client:
            client = MQTTClient({"username": "joe", "password": "doe"})
            mock_client.Client.assert_called_once_with(client_id = f'pipump_12345', clean_session = True, userdata = None, protocol = 4)
            internal_client = mock_client.Client.return_value
            internal_client.username_pw_set.assert_called_once_with(username="joe", password="doe")
    
    def test_attach_pumps_registers_callbacks(self):
        client = MQTTClient({})

        mode_cb = Mock()
        switch_cb = Mock()

        pump1 = Mock()
        pump2 = Mock()
        pumps = [ pump1, pump2 ]

        client.attach(pumps, mode_cb, switch_cb)

        self.assertEqual(client._pumps, pumps)
        for p in pumps:
            p.add_state_callback.assert_called_once()
            p.add_update_callback.assert_called_once()