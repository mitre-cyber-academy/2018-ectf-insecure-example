from psoc import Psoc
import struct
from serial_emulator import HSMEmulator
import logging
import time


class HSM(Psoc):
    """Interface for communicating with the HSM

    Args:
        port (str, optional): Serial port connected to HSM
        verbose (bool, optional): Whether to print debug messages

    Note:
        Calls to get_uuid and withdraw must be alternated to remain in sync
        with the HSM
    """

    def __init__(self, port=None, verbose=False, dummy=False):
        super(HSM, self).__init__('HSM', port, verbose)
        self._vp('Please connect HSM to continue.')
        while not self.connected and not dummy:
            time.sleep(2)
        self._vp('Initialized')

    def _authenticate(self, uuid):
        """Requests authentication from the HSM

        Args:
            uuid (str): Challenge UUID of HSM

        Returns:
            bool: True if HSM verified authentication, False otherwise
        """
        self._vp('Sending UUID %s' % uuid)
        self._push_msg('%s\00' % uuid)

        resp = self._pull_msg()
        self._vp('Received response %s from HSM' % resp)

        return resp == 'K'

    def get_uuid(self):
        """Retrieves the UUID from the HSM

        Returns:
            str: UUID of HSM
        """
        self._sync(False)
        uuid = self._pull_msg()

        if uuid == 'P':
            self._vp('Security module not yet provisioned!', logging.error)
            return None

        self._vp('Got UUID %s' % uuid)

        return uuid

    def withdraw(self, uuid, amount):
        """Attempts to withdraw bills from the HSM

        Args:
            uuid (str): Challenge UUID of HSM
            amount (int): Number of bills to withdraw from HSM

        Returns:
            list of str: List of dispensed bills on success
            str: 'Insufficient funds' if the UUID was incorrect
                 'Not enough bills in ATM' if HSM doesn't have enough bills
                    to complete request
        """
        if not self._authenticate(uuid):
            return 'Insufficient funds'

        msg = struct.pack('B', amount)
        self._push_msg(msg)

        msg = self._pull_msg()
        self._vp('Secmod replied %s' % msg)
        if msg == 'BAD':
            return 'Not enough bills in ATM'

        bills = []
        for i in range(amount):
            bill = self._pull_msg()
            self._vp('Received bill %d/%d: \'%s\'' % (i + 1, amount, bill))

            bills.append(bill)

        return bills

    def provision(self, uuid, bills):
        """Attempts to provision HSM

        Args:
            uuid (str): UUID for HSM
            bills (list of str): List of bills to store in HSM

        Returns:
            bool: True if HSM provisioned, False otherwise
        """
        self._sync(True)

        msg = self._pull_msg()
        if msg != 'P':
            self._vp('HSM already provisioned!', logging.error)
            return False
        self._vp('HSM sent provisioning message')

        self._push_msg('%s\00' % uuid)
        while self._pull_msg() != 'K':
            self._vp('HSM hasn\'t accepted UUID \'%s\'' % uuid, logging.error)
        self._vp('HSM accepted UUID \'%s\'' % uuid)

        self._push_msg(struct.pack('B', len(bills)))
        while self._pull_msg() != 'K':
            self._vp('HSM hasn\'t accepted number of bills', logging.error)
        self._vp('HSM accepted number of bills')

        for bill in bills:
            msg = bill.strip()
            self._vp('Sending bill \'%s\'' % msg.encode('hex'))
            self._push_msg(msg)

            while self._pull_msg() != 'K':
                self._vp('HSM hasn\'t accepted bill', logging.error)
            self._vp('HSM accepted bill')

        self._vp('All bills sent! Provisioning complete!')

        return True


class DummyHSM(HSM):
    """Emulated HSM for testing

    Arguments:
        verbose (bool, optional): Whether to print debug messages
        provision (bool, optional): Whether to start the HSM ready
            for provisioning
    """
    def __init__(self, verbose=False, provision=False):
        ser = HSMEmulator(verbose=verbose, provision=provision)
        super(DummyHSM, self).__init__(port=ser, verbose=verbose, dummy=True)
