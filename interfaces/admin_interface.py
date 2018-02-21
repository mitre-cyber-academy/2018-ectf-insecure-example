""" AdminInterface
This is an example of a client which uses the AdminInterface of the bank server.
The requirements of each method provided by the xmlrpc server are described in
the class docstring.

THIS FILE SHOULD NOT BE CHANGED
"""

import cmd
import socket
import xmlrpclib
import traceback

# The host and port of bank's admin xmlrpc server.
HOST = 'localhost'
PORT = '1338'

ACCOUNT_NAME_MAX_LENGTH = 1024


class AdminInterface(cmd.Cmd):
    """
        The following interface must be supported by the XMLRPC server
        running in your Bank Server.
        ------------------------------------------------------------------------
        function:
            ready_for_atm - check if bank is ready for atms to connect

        args:
            None

        returns:
            bool: True for success, False otherwise.
        ------------------------------------------------------------------------
        function:
            create_account

        args:
            param1 (string - max length 1024): AccountName for created card
            param2 (int): Starting account balance

        returns:
            xmlrpclib base64: Card provisioning material on Success.
            bool: False otherwise.
        ------------------------------------------------------------------------
        function:
            update_balance

        args:
            param1 (string - max length 1024): AccountName of card
            param2 (int): new account balance

        returns:
            bool: True for success, False otherwise.
        ------------------------------------------------------------------------
        function:
            check_balance

        args:
            param1 (string - max length 1024): AccountName of card

        returns:
            int: Account balance on Success.
            bool: False otherwise.
        ------------------------------------------------------------------------
        function:
            create_atm

        args:
            None

        returns:
            xmlrpclib base64:: ATM provisioning material on Success.
            bool: False otherwise.
        ------------------------------------------------------------------------
    """

    intro = 'Welcome to the Admin Interface, type help or ? to list commands.\n'
    prompt = 'admin$ '
    bank_admin = xmlrpclib.ServerProxy('http://' + HOST + ':' + PORT)

    def do_ready_for_atm(self, args):
        """ready_for_atm"""
        try:
            print self.bank_admin.ready_for_atm()
        except socket.error:
            print 'Error connecting to ATM'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_create_account(self, args):
        """create_account <account_name> <amount> <provision material output filename>"""
        try:
            account_name = args.split(' ')[0]
            assert len(account_name) <= ACCOUNT_NAME_MAX_LENGTH
            amount = int(args.split(' ')[1])
            with open(args.split(' ')[2], 'wb') as fp:
                material = self.bank_admin.create_account(account_name, amount).data
                fp.write(material)
            print material

        except socket.error:
            print 'Error connecting to Bank'
        except IndexError:
            print 'Usage: create_account <account_name> <amount> <provision material output filename>'
        except ValueError:
            print 'Amount not an integer'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_update_balance(self, args):
        """update_balance <account_name> <amount>"""
        try:
            account_name = args.split(' ')[0]
            assert len(account_name) <= ACCOUNT_NAME_MAX_LENGTH
            amount = int(args.split(' ')[1])
            print self.bank_admin.update_balance(account_name, amount)
        except socket.error:
            print 'Error connecting to Bank'
        except IndexError:
            print 'Usage: update_balance <account_name> <amount>'
        except ValueError:
            print 'Amount not an integer'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_check_balance(self, args):
        """check_balance <account_name>"""
        try:
            account_name = args.split(' ')[0]
            assert len(account_name) <= ACCOUNT_NAME_MAX_LENGTH
            print self.bank_admin.check_balance(account_name)
        except socket.error:
            print 'Error connecting to Bank'
        except IndexError:
            print 'Usage: check_balance <account_name>'
        except:
            print '**** RECEIVED ERROR ****'
            print traceback.format_exc()

    def do_create_atm(self, args):
        """create_atm <provisioning_material_filename>"""
        try:
            with open(args.split(' ')[0], 'wb') as fp:
                material = self.bank_admin.create_atm().data
                fp.write(material)
            print material
        except socket.error:
            print 'Error connecting to Bank'
        except IndexError:
            print 'Usage: create_atm <provisioning material output filename>'
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
    AdminInterface().cmdloop()
