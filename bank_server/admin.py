""" Bank Server
This module implements the admin access to the database
"""

import db
import cmd


class Admin(cmd.Cmd, object):

    intro = 'Welcome to the Admin Interface, type help or ? to list commands.\n'
    prompt = 'admin$ '

    def __init__(self):
        super(Admin, self).__init__()
        self.db = db.DB()

        if not self.db.exists():
            self.db.init_db()

    def do_add_atm(self, args):
        """Usage: add_atm atm_id"""
        args = args.split(" ")
        if len(args) != 1 or args[0] == '':
            print "Usage: add_atm atm_id"
            return

        if self.db.admin_create_atm(args[0]):
            print "ATM %s added" % args[0]
        else:
            print "ATM add failed!"

    def do_add_card(self, args):
        """Usage: add_card card_id balance"""
        args = args.split(" ")
        if len(args) != 2:
            print "Usage: add_card card_id balance"
            return
        try:
            int(args[1])
        except ValueError:
            print "Error: balance must be a valid integer"


        if self.db.admin_create_account(args[0], args[1]):
            print "Card %s added" % args[0]
        else:
            print "Card add failed!"

    def do_check_balance(self, args):
        """Usage: check_balance card_id"""
        args = args.split(" ")
        if len(args) != 1 or args[0] == '':
            print "Usage: check_balance card_id"
            return

        b = self.db.get_balance(args[0])
        if b:
            print "Card %s balance: %d" % (args[0], int(b))
        else:
            print "Card %s does not exist!" % args[0]

    def do_update_balance(self, args):
        """Usage: update_balance card_id balance"""
        args = args.split(" ")
        if len(args) != 2:
            print "Usage: update_balance card_id balance"
            return

        if self.db.admin_set_balance(args[0], args[1]):
            print "Updated balance"
        else:
            print "Balance update failed!"


if __name__ == "__main__":
    Admin().cmdloop()
