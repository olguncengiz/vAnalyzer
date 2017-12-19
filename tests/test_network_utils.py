"""
Includes all tests for network utils functions.
"""


import sys
sys.path.append('../common')
import unittest
from network_utils import *


class TestGetPort(unittest.TestCase):
    """
    Main test class for get port method
    """

    
    def setUp(self):
        self.http = 'port 80'
        self.https = 'port 443'
        self.s1ap = 'port 36412'
        self.any = ''

    
    def test_port_by_protocol(self):
        self.assertEqual(get_port('http'), self.http)
        self.assertEqual(get_port('https'), self.https)
        self.assertEqual(get_port('s1ap'), self.s1ap)
        self.assertEqual(get_port('ANY'), self.any)


class TestValidateIp(unittest.TestCase):
    """
    Main test class for validate ip method
    """


    def setUp(self):
        self.valid_ip = "192.168.1.1"
        self.local_host = "127.0.0.1"
        self.invalid_ip = "169.254.1.1"

    def test_validate_ip(self):
        self.assertEqual(validate(self.valid_ip), True)
        self.assertEqual(validate(self.local_host), False)
        self.assertEqual(validate(self.invalid_ip), False)


if __name__ == '__main__':
    unittest.main()
