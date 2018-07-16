"""Backend of ATM interface for xmlrpc"""

import logging
import struct


class Bank:
    """Interface for communicating with the bank

    Args:
        port (serial.Serial): Port to connect to
    """

    def __init__(self, port):
        self.port = port

    def check_balance(self, card_id):
        """Requests the balance of the account associated with the card_id

        Args:
            card_id (str): UUID of the ATM card to look up

        Returns:
            str: Balance of account on success
            bool: False on failure
        """
        logging.info('check_balance: Sending request to Bank')
        print card_id
        res = self.bank_rpc.check_balance(card_id)
        if res[:4] == 'OKAY':
            return int(res[5:])
        logging.info('check_balance: Bank request failed %s', res)
        return False

    def withdraw(self, hsm_id, card_id, amount):
        """Requests a withdrawal from the account associated with the card_id

        Args:
            hsm_id (str): UUID of the HSM
            card_id (str): UUID of the ATM card
            amount (str): Requested amount to withdraw

        Returns:
            str: hsm_id on success
            bool: False on failure
        """
        logging.info('withdraw: Sending request to Bank')
        res = self.bank_rpc.withdraw(hsm_id, card_id, amount)
        if res[:4] == 'OKAY':
            return res[5:]
        logging.info('check_balance: Bank request failed %s', res)
        return False

    def provision_update(self, uuid, pin, balance):
        pkt = struct.pack(">36s8sI", uuid, pin, balance)
        self.port.write("p" + pkt)
