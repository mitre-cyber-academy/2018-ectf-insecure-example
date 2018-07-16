from db import DB
import argparse
import serial
import struct


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Serial port to connect to")
    parser.add_argument("--baudrate", type=int, default=115200,
                        help="Baudrate of serial port")
    parser.add_argument("--db-file", default="bank.json",
                        help="Name of bank database file")
    args = parser.parse_args()
    return args.port, args.baudrate, args.db_file


if __name__ == "__main__":
    port, baudrate, db_file = parse_args()

    atm = serial.Serial(port, baudrate, timeout=5)

    try:
        while True:
            print "Listening for provisioning info..."
            while atm.read() != "p":
                continue

            print "Reading provisioning info..."
            pkt = atm.read(48)
            uuid, pin, balance = struct.unpack(">36s8sI", pkt)

            print "Updating database..."
            db = DB(db_file)
            db.admin_create_account(uuid, balance)
            print "Account added!"
            print
    except KeyboardInterrupt:
        print "Shutting down..."
