from Queue import Queue
import logging
import struct


class SerialEmulator(object):
    """Emulates a serial port attached to a PSoC

    Args:
        provision (bool, optional): Whether to start the PSoC in
            provisioning mode. Default skips provisioning
        verbose (bool, optional): Whether to print debugging information

    Note:
        Serial emulators work by maintaining the next function to call in self.next_state. Processing is lazy, so while
        writes add the message to the message queue, self.next_state is only called on reads, as the correct response
        must be calculated.

        To to return a message, return self._return_message, which returns the 1B message header and will return the
        message body on the next call.

        To design your own serial emulator, write down the steps the PSoC would go through, and mark every time it sends
        a message back to the ATM. Every group of steps between send messages becomes a single function.

        Example:
            HSM steps:
                A, B, C, send1, D, send2, send3, send4, E, F, send5, goto B or E based on conditional
            Emulator functions:
                _func1 (A-C, send1) -> _func2 (D, send2) -> _func3 (send3/4) -> _func4 (E-F, send5)

            Example implementation:
                def _func1():
                    # do A
                    return self._func1B

                def _func1B():
                    # do B-C
                    return self._return_msg("message 1", self._func2)

                def _func2():
                    # do D
                    return self._return_msg("message 2", self._func3)

                def _func3():
                    if self.first_call:
                        self.first_call = False
                        return self._return_msg("message 3", self._func3)

                    self.first_call = True
                    return self._return_msg("message 4", self._func4)

                def _func4():
                    # do E-F
                    if conditional:
                        return self._return_msg("message 5", self._func1B)
                    return self._return_msg("message 5", self._func4)

        If the example code message format is kept (i.e. 1B pkt len | pkt ...), then most of this class from write
        through the _send_msg_body method can likely be reused. Shared functions like the reference _sync can be put
        in this class, while card-/HSM-specific functions
    """

    def __init__(self, provision=False, verbose=False):
        self.provision = provision
        self.verbose = verbose
        self.msg_q = Queue()
        self.next_state = self._sync
        self.msg_body = ''
        self.msg_body_next = self._sync
        self.close_on_sync = False
        self.name = None
        self.sync_resp_p = None
        self.sync_resp_n = None
        self.prov_dest = None
        self.sync_dest = None

    def write(self, msg):
        """Write a message to the emulator

               Args:
                   msg (str): message to be sent to the ATM card in proper message format:
                                1B            len(pkt) B
                           | len(pkt) | pkt ...                |
               """
        self.msg_q.put(msg)
        self._vp('Added \'%s\' to the queue' % msg)

    def read(self, b=1, size=0):
        """Reads a message from the emulator

        Args:
            b (doesn't matter): Isn't used

        Returns:
            str: Alternates every call between sending the 1B header and the
                 packet
        """
        self._vp('Going to next state')
        return self.next_state()

    def close(self):
        """Close the serial port and flush the stored commands"""
        self._vp('Flushing commands')
        self.close_on_sync = True
        self.read()
        self._vp('Closing')

    def isOpen(self):
        return True

    def _vp(self, msg, stream=logging.info):
        """Prints message if verbose was set

        Args:
            msg (str): message to print
            stream (logging function, optional): logging function to call
        """
        if self.verbose:
            stream("%s: %s" % (self.name, msg))

    def _next_msg(self):
        """Gets and unformats the next message on the queue

        Returns:
            str: Next message unformatted
        """
        msg = self.msg_q.get()
        msg = struct.unpack("B%ds" % (len(msg) - 1), msg)[1].strip('\00')
        self._vp('Got message \'%s\' from the queue' % msg)
        return msg

    def _return_message(self, msg, next_call):
        """Sends the header and prepares to send the packet on the next
        call to read

        Args:
            msg (str): Raw message to be sent
            next_call (func): State to return to after sending message body

        Returns:
            str: 1B packet header with packet length
        """

        self.next_state = self._send_msg_body
        self.msg_body_next = next_call
        self.msg_body = msg
        self._vp('Returning message header of %d' % len(msg))
        return struct.pack('B', len(msg))

    def _send_msg_body(self):
        """Sends the body of the message and goes to the next state

        Returns:
            str: Packet body
        """

        self.next_state = self.msg_body_next
        self._vp('Returning message body \'%s\'' % self.msg_body)
        return self.msg_body

    def _sync(self):
        """Synchronize communication with ATM

        Returns:
            str: Packet header of sync message
        """

        # don't continue if flushing on close
        if self.close_on_sync:
            return

        msg = self._next_msg()
        if msg != "READY":
            self._vp('ERROR: Sync did not receive correct message! '
                     'Wantedd \'READY\' got \'%s\''
                     % msg)
            return self._return_message(msg, self._sync)

        self._vp('Sync received correct message')
        if self.provision:
            self._vp("Going from sync into provisioning")
            return self._return_message(self.sync_resp_p, self._provision_msg)
        self._vp("Going from sync into normal operation")
        return self._return_message(self.sync_resp_n, self.sync_dest)

    def _sync_complete(self):
        """Finish synchronization process

        Returns:
            bool: Whether synchronization was successful
        """

        msg = self._next_msg()
        if msg != "GO":
            self._vp('ERROR: Sync did not receive correct go message! \'%s\''
                     % msg)
            self.next_state = self._sync
            return False

        self._vp('Sync received correct go message')
        return True

    def _provision_msg(self):
        """Send provisioning message to ATM

        Returns:
            str: Packet header of provisioning message
        """

        if not self._sync_complete():
            return ''

        self._vp('Sending provisioning message')
        return self._return_message("P", self.prov_dest)
