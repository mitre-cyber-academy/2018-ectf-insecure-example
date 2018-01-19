""" DB
This module implements an interface to the bank_server database.
It uses a mutex because both the bank_interface and admin_interface
need access to database. (sqlite3 does not gurantee concurrent operations)"""

import sqlite3
import os

class DB(object):
    """Implements a Database interface for the bank server and admin interface"""
    def __init__(self, db_mutex=None, db_init=None, db_path=None):
        super(DB, self).__init__()
        self.db_conn = sqlite3.connect(os.getcwd() + db_path)
        self.db_mutex = db_mutex
        self.cur = self.db_conn.cursor()
        if db_init and not os.path.isfile(os.getcwd() + db_path):
            self.init_db(os.getcwd() + db_init)

    def close(self):
        """close the database connection"""
        self.db_conn.commit()
        self.db_conn.close()

    def init_db(self, filepath):
        """initialize database with file at filepath"""
        with open(filepath, 'r') as file_handle:
            cmds = file_handle.read().replace('\n', '')
        self.cur.executescript(cmds)
        self.db_conn.commit()

    def lock_db(func):
        """function wrapper for functions that require db access"""
        def func_wrap(self, *args):
            """acquire and release dbMuted if available"""
            if self.db_mutex:
                self.db_mutex.acquire()
            result = func(self, *args)
            self.db_conn.commit()
            if self.db_mutex:
                self.db_mutex.release()
            return result
        return func_wrap

    def modify(self, statement, param):
        """reduce duplicate code"""
        try:
            self.cur.execute(statement, param)
            return True
        except sqlite3.IntegrityError:
            return False

    ############################
    # BANK INTERFACE FUNCTIONS #
    ############################

    @lock_db
    def set_balance(self, card_id, balance):
        """set balance of account: card_id

        Returns:
            (bool): Returns True on Success. False otherwise.
        """
        return self.modify("UPDATE cards SET balance = (?) WHERE \
                                    card_id = (?);", (balance, card_id,))

    @lock_db
    def get_balance(self, card_id):
        """get balance of account: card_id

        Returns:
            (string or None): Returns balance on Success. None otherwise.
        """
        self.cur.execute("SELECT balance FROM cards WHERE card_id = (?);", (card_id,))
        result = self.cur.fetchone()
        if result is None:
            return None
        return result[0]

    @lock_db
    def get_atm(self, atm_id):
        """get atm_id of atm: atm_id
        this is an obviously dumb function but maybe it can be expanded...

        Returns:
            (string or None): Returns atm_id on Success. None otherwise.
        """
        self.cur.execute("SELECT atm_id FROM atms WHERE atm_id = (?);", (atm_id,))
        result = self.cur.fetchone()
        if result is None:
            return None
        return result[0]

    @lock_db
    def get_atm_num_bills(self, atm_id):
        """get number of bills in atm: atm_id

        Returns:
            (string or None): Returns atm_id on Success. None otherwise.
        """
        self.cur.execute("SELECT num_bills FROM atms WHERE atm_id = (?);", (atm_id,))
        result = self.cur.fetchone()
        if result is None:
            return None
        return result[0]

    @lock_db
    def set_atm_num_bills(self, atm_id, num_bills):
        """set number of bills in atm: atm_id

        Returns:
            (bool): Returns True on Success. False otherwise.
        """
        return self.modify("UPDATE atms SET num_bills = (?) WHERE \
                                    atm_id = (?);", (num_bills, atm_id,))

    #############################
    # ADMIN INTERFACE FUNCTIONS #
    #############################

    @lock_db
    def admin_create_account(self, account_name, card_id, amount):
        """create account with account_name, card_id, and amount

        Returns:
            (bool): Returns True on Success. False otherwise.
        """
        return self.modify('INSERT INTO cards(account_name, card_id, balance) \
                            values (?, ?, ?);', (account_name, card_id, amount,))

    @lock_db
    def admin_create_atm(self, atm_id):
        """create atm with atm_id

        Returns:
            (bool): Returns True on Success. False otherwise.
        """
        return self.modify('INSERT INTO atms(atm_id, num_bills) values (?,?);', (atm_id, 128, ))

    @lock_db
    def admin_get_balance(self, account_name):
        """get balance of account: card_id

        Returns:
            (string or None): Returns balance on Success. None otherwise.
        """
        self.cur.execute("SELECT balance FROM cards WHERE account_name = (?);", (account_name,))
        result = self.cur.fetchone()
        if result is None:
            return False
        return result[0]

    @lock_db
    def admin_set_balance(self, account_name, balance):
        """set balance of account: card_id

        Returns:
            (bool): Returns True on Success. False otherwise.
        """
        return self.modify("UPDATE cards SET balance = (?) \
                            WHERE account_name = (?);", (balance, account_name))
