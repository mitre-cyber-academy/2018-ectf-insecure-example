import logging
from interface.psoc import DeviceRemoved, NotProvisioned


class ATM(object):
    """Interface for ATM xmlrpc server

    Args:
        bank (Bank or BankEmulator): Interface to bank
        hsm (HSM or HSMEmulator): Interface to HSM
        card (Card or CardEmulator): Interface to ATM card
    """

    def __init__(self, bank, hsm, card):
        self.bank = bank
        self.hsm = hsm
        self.card = card

    def hello(self):
        logging.info("Got hello request")
        return "hello"

    def check_balance(self, pin):
        """Tries to check the balance of the account associated with the
        connected ATM card

        Args:
            pin (str): 8 digit PIN associated with the connected ATM card

        Returns:
            str: Balance on success
            bool: False on failure
        """
        if not self.card.inserted():
            logging.info('No card inserted')
            return False

        try:
            logging.info('check_balance: Requesting card_id using inputted pin')
            card_id = self.card.check_balance(pin)

            # get balance from bank if card accepted PIN
            if card_id:
                logging.info('check_balance: Requesting balance from Bank')
                res = self.bank.check_balance(card_id)
                if res:
                    return res
            logging.info('check_balance failed')
            return False
        except DeviceRemoved:
            logging.info('ATM card was removed!')
            return False
        except NotProvisioned:
            logging.info('ATM card has not been provisioned!')
            return False

    def change_pin(self, old_pin, new_pin):
        """Tries to change the PIN of the connected ATM card

        Args:
            old_pin (str): 8 digit PIN currently associated with the connected
                ATM card
            new_pin (str): 8 digit PIN to associate with the connected ATM card

        Returns:
            bool: True on successful PIN change
            bool: False on failure
        """
        if not self.card.inserted():
            logging.info('No card inserted')
            return False
        try:
            logging.info('change_pin: Sending PIN change request to card')
            if self.card.change_pin(old_pin, new_pin):
                return True
            logging.info('change_pin failed')
            return False
        except DeviceRemoved:
            logging.info('ATM card was removed!')
            return False
        except NotProvisioned:
            logging.info('ATM card has not been provisioned!')
            return False

    def withdraw(self, pin, amount):
        """Tries to withdraw money from the account associated with the
        connected ATM card

        Args:
            pin (str): 8 digit PIN currently associated with the connected
                ATM card
            amount (int): number of bills to withdraw

        Returns:
            list of str: Withdrawn bills on success
            bool: False on failure
        """
        if not self.hsm.inserted():
            logging.info('No card inserted')
            return False

        if not isinstance(amount, int):
            logging.info('withdraw: amount must be int')
            return False

        try:
            logging.info('withdraw: Requesting card_id from card')
            card_id = self.card.withdraw(pin)

            # request UUID from HSM if card accepts PIN
            if card_id:
                logging.info('withdraw: Requesting hsm_id from hsm')
                hsm_id = self.hsm.get_uuid()

                # request withdrawal from bank if HSM gives UUID
                if hsm_id:
                    logging.info('withdraw: Requesting withdrawal from bank')
                    hsm_id = self.bank.withdraw(hsm_id, card_id, amount)
                    if hsm_id:
                        res = self.hsm.withdraw(hsm_id, amount)
                        if res:
                            return res
                    return False
            logging.info('withdraw failed')
            return False
        except ValueError:
            logging.info('amount must be an int')
            return False
        except DeviceRemoved:
            logging.info('ATM card was removed!')
            return False
        except NotProvisioned:
            logging.info('ATM card has not been provisioned!')
            return False
