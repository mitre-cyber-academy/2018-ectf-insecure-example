""" ProvisioningInterface
This is an example of a client which uses the ProvisioningInterface of the atm.
The requirements of each method provided by the xmlrpc server are described in
the class docstring.

THIS FILE SHOULD NOT BE CHANGED
"""

import cmd
import xmlrpclib
import socket
import traceback

"""
The host and port of atm's xmlrpc server.
"""

HOST = '127.0.0.1'
PORT = '1336'

REQUIRED_PIN_LENGTH = 8
PROVISION_MATERIAL_MAX_SIZE = 16384
BILL_ARRAY_MAX_SIZE = 128
BILL_MAX_SIZE = 16


class ProvisionInterface(cmd.Cmd):
    """
        The following interface must be supported by the XMLRPC server
        running in your ATM Backend.
        ------------------------------------------------------------------------
        function:
            ready_for_hsm - check if atm is ready for hsm to be connected

        args:
            None

        returns:
            bool: True for success, False otherwise.
        ------------------------------------------------------------------------
        function:
            hsm_connected - check if hsm is connected to the atm

        args:
            None

        returns:
            bool: True for success, False otherwise.
        ------------------------------------------------------------------------
        function:
            card_connected - check if a card is connected to the atm

        args:
            None

        returns:
            bool: True for success, False otherwise.
        ------------------------------------------------------------------------
        function:
            provision_card

        args:
            param1 (xmlrpclib base64 - max length 16384 bytes):
                                            Material used to provision card
            param2 (string - required length 8, allowable characters: 0-9):
                                            Pin used to provision card

        returns:
            bool: True for success, False otherwise.
        ------------------------------------------------------------------------
        function:
            provision_atm

        args:
            param1 (xmlrpclib base64 - max length 16384 bytes):
                                            Material used to provision atm
            param2 (string[] - array max length 128, bill string length 16):
                                            Array of bills to provision atm with

        returns:
            bool: True for success, False otherwise.
        ------------------------------------------------------------------------
    """

    intro = 'Welcome to the Provision Client, type help or ? to list commands.\n'
    prompt = 'provision$ '
    atm = xmlrpclib.Server('http://' + HOST + ':' + PORT)

    def do_ready_for_hsm(self, args):
        """hello"""
        try:
            print self.atm.ready_for_hsm()
        except socket.error:
            print 'Error connecting to ATM'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_hsm_connected(self, args):
        """hsm_connected"""
        try:
            print self.atm.hsm_connected()
        except socket.error:
            print 'Error connecting to ATM'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_card_connected(self, args):
        """card_connected"""
        try:
            print self.atm.card_connected()
        except socket.error:
            print 'Error connecting to ATM'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_provision_card(self, args):
        'provision_card <card provision material filename> <pin>'

        try:
            filename = args.split(' ')[0]
            with open(filename) as fp:
                card_provision_material = xmlrpclib.Binary(fp.read().strip(" \n\r"))
            assert len(card_provision_material.data) <= PROVISION_MATERIAL_MAX_SIZE
            pin = args.split(' ')[1].strip(" \n\r")
            print "PIN: " + pin
            assert len(pin) == REQUIRED_PIN_LENGTH
            assert pin.isdigit()
            print self.atm.provision_card(card_provision_material, pin)
        except socket.error:
            print 'Error connecting to ATM'
        except IndexError:
            print 'Usage: provision_card <card provision material filename> <pin>'
        except IOError:
            print traceback.format_exc()
            print(traceback.format_exc().splitlines()[-1])
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_provision_atm(self, args):
        'provision_atm <atm provision material> <billfile name>'
        try:
            provision_material_filename = args.split(' ')[0]
            with open(provision_material_filename) as fp:
                atm_provision_material = xmlrpclib.Binary(fp.read().strip(" \n\r"))
            assert len(atm_provision_material.data) < PROVISION_MATERIAL_MAX_SIZE

            billfile_name = args.split(' ')[1]
            with open(billfile_name) as fp:
                bill_array = fp.readlines()
            print bill_array
            assert all(len(bill.strip(" \n\r")) <= BILL_MAX_SIZE for bill in bill_array)

            print self.atm.provision_atm(atm_provision_material, bill_array)
        except socket.error:
            print 'Error connecting to ATM'
        except IndexError:
            print 'Usage: provision_atm <atm provision material> <bill file>'
        except IOError:
            print traceback.format_exc()
            print(traceback.format_exc().splitlines()[-1])
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_exit(self, args):
        """exit"""
        return 1

    def do_quit(self, args):
        """quit"""
        return 1


if __name__ == '__main__':
    ProvisionInterface().cmdloop()
