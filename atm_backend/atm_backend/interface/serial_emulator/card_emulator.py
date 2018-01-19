from serial_emulator import SerialEmulator
import logging


class CardEmulator(SerialEmulator):
    """Emulates a serial port attached to an ATM card

    Args:
        provision (bool, optional): Whether to start the ATM card in
            provisioning mode. Default skips provisioning
        verbose (bool, optional): Whether to print debugging information
    """

    def __init__(self, provision=False, verbose=False):
        super(CardEmulator, self).__init__(provision, verbose)

        self.name = "CARD EMULATOR"
        self.sync_resp_n = "CARD_N"
        self.sync_resp_p = "CARD_P"
        self.prov_dest = self._get_pin
        self.sync_dest = self._check_pin

        if provision:
            self.pin = ''
            self.uuid = ''
            self._vp('Initialized for provisioning')
        else:
            self.pin = '12345678'
            self.uuid = '0123456789abcdef'
            self._vp('Initialized for normal operation')

    def _get_pin(self):
        """Receives and sets the PIN during provisioning

        Returns:
            str: Packet header of the okay message
        """
        self.pin = self._next_msg()
        self._vp('Received pin \'%s\'' % self.pin)
        return self._return_message("K", self._get_uuid)

    def _get_uuid(self):
        """Receives and sets the UUID of the card during provisioning

        Returns:
            str: Packet header of the okay message
        """
        self.uuid = self._next_msg()
        self._vp('Received UUID \'%s\'' % self.uuid)
        self.provision = False
        return self._return_message("K", self._sync)

    def _check_pin(self):
        """Check sent pin against stored pin

        Returns:
            str: Packet header of either PIN okay or bad message
        """

        if not self._sync_complete():
            return ''

        msg = self._next_msg()
        if msg != self.pin:
            self._vp('ERROR: Got bad PIN (wanted \'%s\' got \'%s\''
                     % (self.pin, msg), logging.error)
            return self._return_message('BAD', self._sync)

        self._vp('Got correct PIN')
        return self._return_message('OK', self._get_command)

    def _get_command(self):
        """Receives the ATM command

        Returns:
            str: Packet header of the okay message
        """
        command = self._next_msg()

        if command == '3':
            return self._return_message('K', self._change_pin)
        return self._return_message('K', self._send_uuid)

    def _send_uuid(self):
        """Send ATM card UUID

        Returns:
            str: Packet header of the UUID message
        """
        self._vp('Sending UUID \'%s\'' % self.uuid)
        return self._return_message(self.uuid, self._sync)

    def _change_pin(self):
        """Change stored pin to sent pin

        Returns:
            str: Packet header of the success message
        """
        self.pin = self._next_msg()
        return self._return_message("SUCCESS", self._sync)
