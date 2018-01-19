from unittest import TestCase
from serial import Serial
from .. import Card
from subprocess import Popen
from admin_connection import AdminConnection
from atm_connection import ATMConnection
import os, yaml, time


class TestCard(TestCase):
    @classmethod
    def setUpClass(cls):
        # Load configuration yaml
        config_path = os.path.join(os.path.dirname(__file__), 'test_config.yaml')
        with open(config_path, 'r') as ymlfile:
            config = yaml.load(ymlfile)
        cls.config = config

        # Connect to bank and admin interfaces
        cls.admin_iface = AdminConnection(config)
        cls.atm_iface = ATMConnection(config)

        cls.bills = ['Example Bill 000', 'Example Bill 001', 'Example Bill 002',
                 'Example Bill 003', 'Example Bill 004', 'Example Bill 005',
                 'Example Bill 006', 'Example Bill 007', 'Example Bill 008',
                 'Example Bill 009', 'Example Bill 00a', 'Example Bill 00b',
                 'Example Bill 00c', 'Example Bill 00d', 'Example Bill 00e',
                 'Example Bill 00f']

        cls.account_name = 'martha'
        cls.amount = 400
        cls.pin = '12345678'

    @classmethod
    def tearDownClass(cls):
        pass

    def test_check_balance_invalid_pin(self):
        self.card_id = self.admin_iface.create_account(self.account_name, self.amount)
        self.assertTrue(self.card_id)

        self.atm_id = self.admin_iface.create_atm()
        self.assertTrue(self.atm_id)

        res = self.atm_iface.provision_atm(self.atm_id, self.bills)
        self.assertTrue(res)

        res = self.atm_iface.provision_atm(self.atm_id, self.bills)
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.provision_card(self.card_id, self.pin)
        self.assertTrue(res)

        res = self.atm_iface.provision_card(self.card_id, self.pin)
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.check_balance(self.pin)
        self.assertTrue(isinstance(res, int))
        self.assertTrue(res == 400)

        res = self.atm_iface.check_balance('11111111')
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.check_balance('111111111')
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.withdraw(self.pin, 5)
        self.assertTrue(isinstance(res, list))
        self.assertTrue(res == self.bills[:5])

        res = self.atm_iface.withdraw(self.pin, '5')
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.withdraw('11111111', 5)
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.withdraw('111111111', 5)
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        self.pin = '87654321'
        res = self.atm_iface.change_pin('12345678', self.pin)
        print res
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == True)

        res = self.atm_iface.change_pin('12345678', self.pin)
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.check_balance(self.pin)
        self.assertTrue(isinstance(res, int))
        self.assertTrue(res == 395)

        res = self.atm_iface.check_balance('11111111')
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.check_balance('111111111')
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.withdraw(self.pin, 5)
        self.assertTrue(isinstance(res, list))
        self.assertTrue(res == self.bills[5:10])

        res = self.atm_iface.withdraw(self.pin, '5')
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.withdraw('11111111', 5)
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)

        res = self.atm_iface.withdraw('111111111', 5)
        self.assertTrue(isinstance(res, bool))
        self.assertTrue(res == False)
