""" ATMInterface
This is an example of a client which uses the ATMInterface of the atm.
The requirements of each method provided by the xmlrpc server are described in
the class docstring.

THIS FILE SHOULD NOT BE CHANGED
"""

import cmd
import xmlrpclib
import socket
import traceback


"""
The host and port of atm xmlrpc server.
"""
HOST = '127.0.0.1'
PORT = '1336'

REQUIRED_PIN_LENGTH = 8


class ATMInterface(cmd.Cmd):
    """
        The following interface must be supported by the XMLRPC server
        running in your ATM Backend.

        ------------------------------------------------------------------------
        function:
            withdraw

        args:
            param1 (string - required length 8, allowable characters: 0-9): Card pin
            param2 (int - max number of bills supported by atm ): Amount to withdraw

        returns:
            bool: True for success, False otherwise.
        ------------------------------------------------------------------------
        function:
            check_balance

        args:
            param1 (string - required length 8, allowable characters: 0-9): Card pin

        returns:
            int: Balance for success.
            bool: False otherwise.
        ------------------------------------------------------------------------
        function:
            change_pin

        args:
            param1 (string - required length 8, allowable characters: 0-9): Old card pin
            param1 (string - required length 8, allowable characters: 0-9): New card pin

        returns:
            bool: The return value. True for success, False otherwise.
        ------------------------------------------------------------------------
    """

    intro = 'Welcome to the ATM Interface, type help or ? to list commands.\n'
    prompt = 'atm$ '
    atm = xmlrpclib.ServerProxy('http://' + HOST + ':' + PORT)

    def do_hello(self, args):
        """hello"""
        try:
            print self.atm.hello()
        except socket.error:
            print 'Error connecting to ATM'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_withdraw(self, args):
        """withdraw <pin> <amount>"""
        try:
            pin = args.split(' ')[0]
            amount = int(args.split(' ')[1])
            assert len(pin) == REQUIRED_PIN_LENGTH and pin.isdigit()
            if amount <= 0:
                raise UserWarning
            res = self.atm.withdraw(pin, amount)
            if not res:
                print 'withdraw failed'
            else:
                print res
        except socket.error:
            print 'Error connecting to ATM'
        except IndexError:
            print 'Usage: withdraw <pin> <amount>'
        except AssertionError:
            print 'Invalid pin'
        except ValueError:
            print 'Amount not an integer'
        except UserWarning:
            print 'Invalid amount'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_check_balance(self, args):
        """check_balance <pin>"""
        try:
            if len(args) == 0:
                raise UserWarning
            pin = args.split(' ')[0]
            assert len(pin) == REQUIRED_PIN_LENGTH and pin.isdigit()
            res = self.atm.check_balance(pin)
            if not res:
                print 'check_balance failed'
            else:
                print res
        except socket.error:
            print 'Error connecting to ATM'
        except UserWarning:
            print 'Usage: check_balance <pin>'
        except AssertionError:
            print 'Invalid pin'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_change_pin(self, args):
        """change_pin <old_pin> <new_pin>"""
        try:
            old_pin = args.split(' ')[0]
            new_pin = args.split(' ')[1]
            assert len(old_pin) == REQUIRED_PIN_LENGTH and old_pin.isdigit()
            assert len(new_pin) == REQUIRED_PIN_LENGTH and new_pin.isdigit()
            res = self.atm.change_pin(old_pin, new_pin)
            if not res:
                print 'change_pin failed'
            else:
                print res
        except socket.error:
            print 'Error connecting to ATM'
        except IndexError:
            print 'Usage: change_pin <old_pin> <new_pin>'
        except AssertionError:
            print 'Invalid pin'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def emptyline(self):
        pass

    def do_exit(self, args):
        """exit"""
        return 1

    def do_quit(self, args):
        """quit"""
        return 1


if __name__ == '__main__':
    ATMInterface().cmdloop()
