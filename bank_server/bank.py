""" Bank Server
This module implements a bank server interface
"""

import uuid
import db
import logging
from logging import info as log
import sys
import serial
import argparse
import struct


class Bank(object):
    GOOD = "O"
    BAD = "N"
    ERROR = "E"

    def __init__(self, port, baud=115200, db_path="bank.json"):
        super(Bank, self).__init__()
        self.db = db.DB(db_path=db_path)
        self.atm = serial.Serial(port, baudrate=baud, timeout=10)

    def start(self):
        while True:
            command = self.atm.read()
            if command == 'b':
                log("Checking balance")
                pkt = self.atm.read(76)
                atm_id, card_id, amount = struct.unpack(">36s36sI", pkt)
                self.withdraw(atm_id, card_id, amount)
            elif command == 'w':
                log("Withdrawing")
                pkt = self.atm.read(72)
                atm_id, card_id = struct.unpack(">36s36s", pkt)
                self.check_balance(atm_id, card_id)
            elif command != '':
                self.atm.write(self.ERROR)

    def withdraw(self, atm_id, card_id, amount):
        try:
            amount = int(amount)
            atm_id = str(atm_id)
            card_id = str(card_id)
        except ValueError:
            self.atm.write(self.ERROR)
            log("Bad value sent")
            return

        atm = self.db.get_atm(atm_id)
        if atm is None:
            self.atm.write(self.ERROR)
            log("Bad ATM ID")
            return

        num_bills = self.db.get_atm_num_bills(atm_id)
        if num_bills is None:
            self.atm.write(self.ERROR)
            log("Bad ATM ID")
            return

        if num_bills < amount:
            self.atm.write(self.BAD)
            log("Insufficient funds in ATM")
            return

        balance = self.db.get_balance(card_id)
        if balance is None:
            self.atm.write(self.BAD)
            log("Bad card ID")
            return

        final_amount = balance - amount
        if final_amount >= 0:
            self.db.set_balance(card_id, final_amount)
            self.db.set_atm_num_bills(atm_id, num_bills - amount)
            log("Valid withdrawal")
            pkt = struct.pack(">36s36sI", atm_id, card_id, amount)
            self.atm.write(self.GOOD)
            self.atm.write(pkt)
        else:
            self.atm.write(self.BAD)
            log("Insufficient funds in account")

    def check_balance(self, atm_id, card_id):
        if self.db.get_atm(atm_id) is None:
            self.atm.write(self.BAD)
            log("Invalid ATM ID")
            return

        balance = self.db.get_balance(str(card_id))
        if balance is None:
            self.atm.write(self.BAD)
            log("Bad card ID")
        else:
            log("Valid balance check")
            pkt = struct.pack(">36s36sI", atm_id, card_id, balance)
            self.atm.write(self.GOOD)
            self.atm.write(pkt)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Serial port ATM is connected to")
    parser.add_argument("--baudrate", help="Optional baudrate (default 115200)")
    return parser.parse_args()


def main():
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(log_format)
    log.addHandler(ch)

    args = parse_args()

    bank = Bank(args.port, args.baudrate)
    try:
        bank.start()
    except KeyboardInterrupt:
        print "Shutting down bank..."


if __name__ == "__main__":
    main()
