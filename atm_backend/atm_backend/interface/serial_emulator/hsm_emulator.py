import struct
from Queue import Queue
from serial_emulator import SerialEmulator
import logging


class HSMEmulator(SerialEmulator):
    """Emulates a serial port attached to an HSM

    Args:
        provision (bool, optional): Whether to start the HSM in
            provisioning mode. Default skips provisioning
        verbose (bool, optional): Whether to print debugging information
    """

    def __init__(self, provision=False, verbose=False):
        super(HSMEmulator, self).__init__(provision, verbose)
        self.bills = Queue()

        self.name = "HSM EMULATOR"
        self.sync_resp_n = "HSM_N"
        self.sync_resp_p = "HSM_P"
        self.prov_dest = self._get_uuid
        self.sync_dest = self._send_uuid
        self.to_dispense = -1

        if provision:
            self.uuid = ""
            self.bill_count = 0
            self._vp('Initialized for provisioning')
        else:
            self.uuid = "beefcafebeefcafe"
            self.bill_count = 128
            for n in range(128):
                self.bills.put('Example Bill %d' % n)
            self._vp('Initialized for normal operation')

    def _get_uuid(self):
        """Receives and sets the UUID of the HSM during provisioning

        Returns:
            str: Packet header of the okay message
        """
        self.uuid = self._next_msg()
        self._vp('Received UUID \'%s\'' % self.uuid)
        return self._return_message('K', self._get_numbills)

    def _get_numbills(self):
        """Receives and sets the number of bills on the HSM

        Returns:
            str: Packet header of the okay message
        """
        self.bill_count = struct.unpack('B', self._next_msg())[0]
        self.bills_left = self.bill_count
        self._vp('Received numbills \'%s\'' % self.bill_count)
        return self._return_message('K', self._load_bill)

    def _load_bill(self):
        """Receives and adds a single bill to the HSM

        Returns:
            str: Packet header of the okay message
        """
        bill = self._next_msg()
        self.bills.put(bill)
        self._vp('Loaded bill \'%s\'' % bill)

        self.bill_count -= 1
        if self.bill_count == 0:
            self.provision = False
            self._vp('Provisioning done!')
            return self._return_message('K', self._sync)

        return self._return_message('K', self._load_bill)

    def _send_uuid(self):
        """Send HSM UUID

        Returns:
            str: Packet header of the UUID message
        """
        if not self._sync_complete():
            return ''

        self._vp('Sending UUID %s' % self.uuid)
        return self._return_message(self.uuid, self._check_uuid)

    def _check_uuid(self):
        """Check sent UUID against stored UUID

        Returns:
            str: Packet header of either UUID okay or bad message
        """
        hsmid = self._next_msg()

        if hsmid != self.uuid:
            self._vp("ERROR: got bad UUID (wanted \'%s\' got \'%s\'"
                     % (self.uuid, hsmid), logging.error)
            return self._return_message('BAD', self._sync)
        return self._return_message('K', self._dispense_bills)

    def _dispense_bills(self):
        """Dispenses one bill from the HSM storage

        Returns:
            str: Packet header of a dispensed bill
        """
        if self.to_dispense == 0:
            self.to_dispense = -1
            self._vp('Done dispensing bills')
            return self._sync()

        if self.to_dispense == -1:
            self.to_dispense = struct.unpack("B", self._next_msg())[0]
            if self.to_dispense > self.bills_left:
                self.to_dispense = -1
                return self._return_message("BAD", self._sync)

            self._vp('Ready to dispense %d bills' % self.to_dispense)
            return self._return_message('K', self._dispense_bills)

        self.bills_left -= 1
        self.to_dispense -= 1
        bill = self.bills.get()
        self._vp('Dispensing bill \'%s\'' % bill)
        return self._return_message(bill, self._dispense_bills)
