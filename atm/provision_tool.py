from interface.card import Card
from interface.bank import Bank
from os import urandom
import argparse
import serial


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("balance", type=int,
                        help="Starting balance for account")
    parser.add_argument("cport", help="Serial port to the card")
    parser.add_argument("bport", help="Serial port to the bank")
    parser.add_argument("--cbaud", type=int, default=115200,
                        help="Baudrate of serial connection to the card")
    parser.add_argument("--bbaud", type=int, default=115200,
                        help="Baudrate of serial connection to the bank")
    parser.add_argument("--pin", default="12345678",
                        help="Initial pin to program (default 12345678)")
    args = parser.parse_args()
    return args.balance, args.cport, args.bport, args.cbaud, args.bbaud, args.pin


if __name__ == "__main__":
    balance, c_port, b_port, c_baud, b_baud, pin = parse_args()

    # provision card
    print "Provisioning card..."
    card = Card(c_port, baudrate=c_baud, verbose=True)
    uuid = urandom(18).encode("hex")
    if card.provision(uuid, pin):
        print "Card provisioned!"

        # update bank
        print "Updating bank..."
        bank = Bank(serial.Serial(b_port, b_baud))
        bank.provision_update(uuid, pin, balance)
        print "Provisioning successful"
    else:
        print "Card already provisioned!"

