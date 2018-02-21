import struct
import time
import logging
import threading
import serial
import sys
import os
from serial.tools.list_ports import comports as list_ports


class DeviceRemoved(Exception):
    pass


class NotProvisioned(Exception):
    pass


class AlreadyProvisioned(Exception):
    pass


class Psoc(object):
    """Generic PSoC communication interface

    Args:
        name (str): Name of the PSoC for debugging
        ser (serial.Serial or serial emulator): Serial interface for
            communication
        verbose (bool): Controls printing of debug messages
    """

    def __init__(self, name, ser, verbose):
        log = sys.stdout if verbose else open(os.devnull, 'w')
        logging.basicConfig(stream=log, level=logging.DEBUG)
        self.ser = ser
        self.verbose = verbose
        self.fmt = '%s: %%s' % name
        self.name = name
        self.lock = threading.Lock()
        self.connected = False
        self.port = ''
        self.baudrate = 115200
        self.old_ports = [port_info.device for port_info in list_ports()]
        self.sync_name_n = '%s_N' % name
        self.sync_name_p = '%s_P' % name

        if ser:
            self.connected = True
        else:
            self.start_connect_watcher()

    def _vp(self, msg, stream=logging.info):
        """Prints message if verbose was set

        Args:
            msg (str): message to print
            stream (logging function, optional): logging function to call
        """
        if self.verbose:
            stream(self.fmt % msg)

    def _push_msg(self, msg):
        """Sends formatted message to PSoC

        Args:
            msg (str): message to be sent to the PSoC
        """
        pkt = struct.pack("B%ds" % (len(msg)), len(msg), msg)
        self.write(pkt)
        time.sleep(0.1)

    def _pull_msg(self):
        """Pulls message form the PSoC

        Returns:
            string with message from PSoC
        """
        hdr = self.read(1)
        if len(hdr) != 1:
            self._vp("RECEIVED BAD HEADER: \'%s\'" % hdr, logging.error)
            return ''
        pkt_len = struct.unpack('B', hdr)[0]
        return self.read(pkt_len)

    def _sync_once(self, names):
        resp = ''
        while resp not in names:
            self._vp('Sending ready message')
            self._push_msg("READY\00")
            resp = self._pull_msg()
            self._vp('Got response \'%s\', want something from \'%s\'' % (resp, str(names)))

            # if in wrong state (provisioning/normal)
            if len(names) == 1 and resp != names[0] and resp[:-1] == names[0][:-1]:
                return False

        return resp

    def _sync(self, provision):
        """Synchronize communication with PSoC

        Args:
            provision (bool): Whether expecting unprovisioned state

        Raises:
            NotProvisioned if PSoC is unexpectedly unprovisioned
            AlreadyProvisioned if PSoC is unexpectedly already provisioned
        """
        if provision:
            if not self._sync_once([self.sync_name_p]):
                self._vp("Already provisioned!", logging.error)
                raise AlreadyProvisioned
        else:
            if not self._sync_once([self.sync_name_n]):
                self._vp("Not yet provisioned!", logging.error)
                raise NotProvisioned
        self._push_msg("GO\00")
        self._vp("Connection synced")

    def open(self):
        time.sleep(.1)
        self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=1)
        resp = self._sync_once(['CARD_N', 'CARD_P', 'HSM_N', 'HSM_P'])
        if resp == self.sync_name_p or resp == self.sync_name_n:
            logging.info('DYNAMIC SERIAL: Connected to %s', resp)
            self.connected = True
        else:
            logging.info('DYNAMIC SERIAL: Expected %s or %s', self.sync_name_p,
                                                              self.sync_name_n)
            logging.info('DYNAMIC SERIAL: Disconnecting from %s', resp)
            self.start_connect_watcher()

    def device_connect_watch(self):
        """Threaded function that connects to new serial devices"""

        # Read current ports
        connecting = []

        # Has a new device connected?
        while len(connecting) == 0:
            new_ports = [port_info.device for port_info in list_ports()]
            connecting = list(set(new_ports) - set(self.old_ports))
            self.old_ports = new_ports
            time.sleep(.25)
        self.port = connecting[0]
        logging.info("DYNAMIC SERIAL: Found new serial device")
        self.open()
        if self.name == 'CARD':
            self.start_disconnect_watcher()

    def device_disconnect_watch(self):
        """Threaded function that connects to new serial devices"""

        # Read current ports
        disconnecting = []

        # Has a new device connected?
        while not disconnecting and self.port not in disconnecting:
            new_ports = [port_info.device for port_info in list_ports()]
            disconnecting = list(set(self.old_ports) - set(new_ports))
            self.old_ports = new_ports

        logging.info("DYNAMIC SERIAL: %s disconnected", self.name)
        self.port = ''
        self.connected = False
        self.lock.acquire()
        self.ser.close()
        self.lock.release()
        self.start_connect_watcher()

    def read(self, size=1):
        """Reads bytes from the connected serial device

        Args:
            size (int, optional): The number of bytes to read from the serial
                device. Defaults to reading one byte.

        Returns:
            str: Buffer of bytes read from device

        Raises:
            DeviceRemoved: If the Device was removed before or during read
        """
        try:
            self.lock.acquire()
            res = self.ser.read(size=size)
            self.lock.release()
            return res
        except serial.SerialException:
            self.connected = False
            self.ser.close()
            self.lock.release()
            self.start_connect_watcher()
            raise DeviceRemoved

    def write(self, data):
        """Writes bytes to the connected serial device

        Args:
            data (str): The bytes to be written to the serial device

        Raises:
            DeviceRemoved: If the Device was removed before or during write
        """
        try:
            self.lock.acquire()
            res = self.ser.write(data)
            self.lock.release()
            return res
        except serial.SerialException:
            self.connected = False
            self.ser.close()
            self.lock.release()
            self.start_connect_watcher()
            raise DeviceRemoved

    def start_connect_watcher(self):
        logging.info("DYNAMIC SERIAL: Closed serial and spun off %s-connect-watcher thread", self.name)
        self.old_ports = [port_info.device for port_info in list_ports()]
        threading.Thread(target=self.device_connect_watch, name="%s-watcher" % self.name).start()

    def start_disconnect_watcher(self):
        logging.info("DYNAMIC SERIAL: Opened serial and spun off %s-disconnect-watcher thread", self.name)
        self.old_ports = [port_info.device for port_info in list_ports()]
        threading.Thread(target=self.device_disconnect_watch, name="%s-disconnect-watcher" % self.name).start()

    def inserted(self):
        """Queries if serial port to ATM card is open

        Returns:
            bool: True if port is open, False otherwise
        """
        return self.ser.isOpen()

    def wait_for_insert(self):
        """Blocks until a card is dynamically acquired"""
        self._vp('Waiting for card insertion')
        while not self.ser:
            time.sleep(.25)
        while not self.ser.isOpen():
            time.sleep(.25)
