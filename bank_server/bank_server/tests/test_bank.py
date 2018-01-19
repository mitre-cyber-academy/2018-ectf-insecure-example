from unittest import TestCase
from multiprocessing import Process
from bank_server import Bank, DB, AdminBackend
from bank_connection import BankConnection
from admin_connection import AdminConnection
import sys, os, yaml, threading, time
import uuid

class TestBank(TestCase):
    # Create listening socket for bank testing
    @classmethod
    def setUpClass(cls):
        # Load configuration yaml
        config_path = os.path.join(os.path.dirname(__file__), 'test_config.yaml')
        with open(config_path, 'r') as ymlfile:
            config = yaml.load(ymlfile)
        cls.config = config
        # Create database mutex for Bank and AdminBackend
        db_mutex = threading.Lock()

        # Run bank and its admin interface
        cls.bank = Process(target=Bank, args=(config, db_mutex))
        cls.admin = Process(target=AdminBackend, args=(config, db_mutex))
        cls.bank.start()
        cls.admin.start()

        # Wait for bank and admin interface to initialize
        time.sleep(3)

        # Connect to bank and admin interfaces
        cls.admin_iface = AdminConnection(config)

    @classmethod
    def tearDownClass(cls):
        print "Must kill test manually"
        cls.bank.terminate()
        cls.admin.terminate()

    def test_check_balance_valid(self):
        bank_iface = BankConnection(self.config)
        card_id = str(uuid.UUID('{50000000-0000-0000-0000-000000000000}'))
        res = bank_iface.check_balance(card_id)
        print 'output'
        print res
        print self.config
        print 'output'
        self.assertTrue(res[:4] == 'OKAY')
        self.assertTrue(int(res[5:]) == 10)

    def test_check_balance_invalid_card_id(self):
        bank_iface = BankConnection(self.config)
        card_id = str(uuid.UUID('{53000000-0000-0000-0000-000000000000}'))
        res = bank_iface.check_balance(card_id)
        print res
        self.assertTrue(res[:5] == 'ERROR')
        self.assertTrue(res[6:] == 'could not lookup account \''+card_id+'\'')

    def test_check_balance_invalid_command(self):
        bank_iface = BankConnection(self.config)
        card_id = '111      '
        res = bank_iface.check_balance(card_id)
        self.assertTrue(res[:5] == 'ERROR')
        self.assertTrue(res[6:] == 'check_balance command usage: balance <card_id>')

    def test_withdraw_valid(self):
        bank_iface = BankConnection(self.config)
        # atm,card,amount
        atm_id = str(uuid.UUID('{40000000-0000-0000-0000-000000000000}'))
        card_id = str(uuid.UUID('{50000000-0000-0000-0000-000000000000}'))
        amount = '3'
        res = bank_iface.withdraw(atm_id, card_id, amount)
        self.assertTrue(res[:4] == 'OKAY')

    def test_withdraw_invalid_atm_id(self):
        bank_iface = BankConnection(self.config)
        # atm,card,amount
        atm_id = str(uuid.UUID('{99900000-0000-0000-0000-000000000000}'))
        card_id = str(uuid.UUID('{50000000-0000-0000-0000-000000000000}'))
        amount = '3'
        res = bank_iface.withdraw(atm_id, card_id, amount)
        self.assertTrue(res[:5] == 'ERROR')
        self.assertTrue(res[6:] == 'could not lookup atm \'%s\'' % atm_id)

    def test_withdraw_invalid_card_id(self):
        bank_iface = BankConnection(self.config)
        # atm,card,amount
        atm_id = str(uuid.UUID('{40000000-0000-0000-0000-000000000000}'))
        card_id = str(uuid.UUID('{88800000-0000-0000-0000-000000000000}'))
        amount = '3'
        res = bank_iface.withdraw(atm_id, card_id, amount)
        self.assertTrue(res[:5] == 'ERROR')
        self.assertTrue(res[6:] == 'could not lookup card \'%s\'' % card_id)

    def test_withdraw_invalid_amount(self):
        bank_iface = BankConnection(self.config)
        # atm,card,amount
        atm_id = str(uuid.UUID('{40000000-0000-0000-0000-000000000000}'))
        card_id = str(uuid.UUID('{50000000-0000-0000-0000-000000000000}'))
        amount = '777'
        res = bank_iface.withdraw(atm_id, card_id, amount)
        print res
        print res[6:37]
        self.assertTrue(res[:5] == 'ERROR')
        self.assertTrue(res[6:31] == 'insufficient funds in atm')

    def test_withdraw_invalid_command(self):
        bank_iface = BankConnection(self.config)
        res = bank_iface.withdraw('a', 'b', 'c')
        self.assertTrue(res[:5] == 'ERROR')
        self.assertTrue(res[6:] == 'withdraw command usage: withdraw <atm_id> <card_id> <amount>')


    def test_admin_create_account_valid(self):
        account_name = 'test acav'
        amount = '5'
        res = self.admin_iface.create_account(account_name, amount)
        self.assertTrue(res)
        res = self.admin_iface.check_balance('test acav')
        self.assertTrue(res == 5)

    def test_admin_create_account_invalid_duplicate_acct_name(self):
        account_name = 'richard'
        amount = '5'
        res = self.admin_iface.create_account(account_name, amount)
        self.assertTrue(res)
        res = self.admin_iface.create_account(account_name, amount)
        print res
        self.assertFalse(res)

    def test_admin_create_account_invalid_duplicate_card_name(self):
        account_name = 'loral'
        amount = '56'
        res = self.admin_iface.create_account(account_name, amount)
        self.assertTrue(res)
        account_name = 'loralli'
        res = self.admin_iface.create_account(account_name, amount)
        print res
        self.assertFalse(res == '00000000-0000-0000-0000-000000000000')

    def test_admin_create_account_invalid_amount(self):
        account_name = 'cheryl'
        amount = 'a'
        res = self.admin_iface.create_account(account_name, amount)
        self.assertFalse(res)

    def test_admin_update_balance_valid(self):
        account_name = 'gerald'
        amount = '10'
        res = self.admin_iface.create_account(account_name, amount)
        res = self.admin_iface.check_balance(account_name)
        self.assertTrue(res == 10)
        print self.admin_iface.update_balance('gerald', 15)
        res = self.admin_iface.check_balance('gerald')
        self.assertTrue(res == 15)

    def test_admin_check_balance_valid(self):
        account_name = 'myrtle'
        amount = '20'
        res = self.admin_iface.create_account(account_name, amount)
        res = self.admin_iface.check_balance(account_name)
        self.assertTrue(res == 20)

    def test_admin_create_atm_valid(self):
        res = self.admin_iface.create_atm()
        self.assertTrue(res)

    def test_all(self):
        bank_iface = BankConnection(self.config)
        account_name = 'marsha'
        amount = '57'
        card_id = self.admin_iface.create_account(account_name, amount)
        self.assertTrue(card_id)

        bal = self.admin_iface.check_balance('marsha')
        self.assertTrue(bal == 57)

        card_id_inv = self.admin_iface.create_account(account_name, amount)
        self.assertTrue(card_id_inv == False)

        res = bank_iface.check_balance(card_id)
        self.assertTrue(int(res[5:]) == 57)

        atm_id = self.admin_iface.create_atm()
        self.assertTrue(res)

        bal = self.admin_iface.check_balance('marsha')
        self.assertTrue(bal == 57)

        res = bank_iface.withdraw(atm_id, card_id, 57)
        self.assertTrue(res[:4] == 'OKAY')

        bal = self.admin_iface.check_balance('marsha')
        self.assertTrue(bal == 0)

        self.admin_iface.update_balance('marsha', 15)
        bal = self.admin_iface.check_balance('marsha')
        self.assertTrue(bal == 15)


    def test_overdraw_atm(self):
        bank_iface = BankConnection(self.config)
        account_name = 'martha'
        amount = '400'
        card_id = self.admin_iface.create_account(account_name, amount)
        self.assertTrue(card_id)

        bal = self.admin_iface.check_balance('martha')
        self.assertTrue(bal == 400)

        card_id_inv = self.admin_iface.create_account(account_name, amount)
        self.assertTrue(card_id_inv == False)

        res = bank_iface.check_balance(card_id)
        self.assertTrue(int(res[5:]) == 400)

        atm_id = self.admin_iface.create_atm()
        self.assertTrue(res)

        bal = self.admin_iface.check_balance('martha')
        self.assertTrue(bal == 400)

        res = bank_iface.withdraw(atm_id, card_id, 400)
        self.assertTrue(res[:5] == 'ERROR')
        print res
        bal = self.admin_iface.check_balance('martha')
        self.assertTrue(bal == 400)
