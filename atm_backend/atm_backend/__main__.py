"""Initializes the XML-RPC server for provisioning and ATM operation

Module structure:
    XML-RPC server started in __main__.py with functions from the following
    files:
        - atm.py
        - provision_tool.py

    The ATM and provision tool use the Bank, HSM, and Card classes from
    ./interfaces to communicate with their real-world components or can use the
    DummyBank, DummyHSM, and DummyCard from ./interfaces to emulate the
    behavior of each without PSoCs or a bank server, allowing for isolated
    testing of each real component.

    Instead of using pyserial, DummyHSM and DummyBank each use a SerialEmulator
    from ./interface/serial_emulator, which emulate the behavior of a serial
    port attached to a PSoC HSM or card.


config.yaml:
    Holds configuration data for atm_backend, including which components to
    use dummy interfaces for, IPs and ports to expose the XML-RPC server over
    and for connecting to the bank, the location of the log file, and verbosity
    of the log file debug messages.

Available XML-RPC functions:
    check_balance:
        Tries to check the balance of the account associated with the
            connected ATM card

        Args:
            pin (str): 8 digit PIN associated with the connected ATM card

        Returns:
            str: Balance on success
                 'No card inserted' if no ATM card is connected at call
                 'ATM card was removed!' if ATM card was removed during call
                 'failure' if ATM card rejected PIN

    change_pin:
        Tries to change the PIN of the connected ATM card

        Args:
            old_pin (str): 8 digit PIN currently associated with the connected
                ATM card
            new_pin (str): 8 digit PIN to associate with the connected ATM card

        Returns:
            str: 'success' on successful PIN change
                 'No card inserted' if no ATM card is connected at call
                 'ATM card was removed!' if ATM card was removed during call
                 'failure' if card rejected PIN

    withdraw:
        Tries to withdraw money from the account associated with the
            connected ATM card

        Args:
            pin (str): 8 digit PIN currently associated with the connected
                ATM card
            amount (str): number of bills to withdraw

        Returns:
            list of str: Withdrawn bills on success
            str:
                 'No card inserted' if no ATM card is connected at call
                 'ATM card was removed!' if ATM card was removed during call
                 'failure' if card rejected PIN or proceeding would overdraw
                    from account

    provision_card:
        Attempts to provision an ATM card

        Args:
            card_blob (str): Provisioning data for the ATM card
            pin (str): Initial PIN for the card

        Returns:
            str: 'success' on success
                 'No card inserted' if no ATM card is connected at call
                 'ATM card was removed!' if ATM card was removed during call
                 'failure' if ATM card failed during provisioning

    provision_atm:
        Attempts to provision an HSM

        Args:
            hsm_blob (str): Provisioning data for the HSM
            bills (list of str): List of bills to be stored in the HSM

        Returns:
            str: 'success' on success
                 'failure' if HSM failed during provisioning
"""

import os
import logging
from logging import handlers
import sys
import SimpleXMLRPCServer
import yaml
from . import ATM, ProvisionTool
from . import Bank, Card, HSM, DummyBank, DummyCard, DummyHSM


def main():
    # Get configuration yaml
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    # Setup logging based on verbosity flag in config.yaml
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(log_format)
    log.addHandler(ch)

    if config['verbose']:
        log_path = os.path.dirname(__file__) + config['logging']['log_path']
        fh = handlers.RotatingFileHandler("%s/%s.log" % (log_path, config['logging']['log_name']), backupCount=7)
        fh.setFormatter(log_format)
        log.addHandler(fh)

    # Create Bank object which creates connection with bank server
    # a dummy counterpart is also available for use
    logging.info('Initializing Bank...')
    if config['devices']['bank']['dummy']:
        bank = DummyBank()
    else:
        bank = Bank(config['devices']['bank']['host'],
                    config['devices']['bank']['port'])
    logging.info('Bank initialized.')

    # Create secmod object which creates connection with secmod psoc
    # a emulated counterpart is also available for use
    if config['devices']['hsm']['dummy']:
        logging.info('Initializing DummyHSM ')
        hsm = DummyHSM(verbose=config['verbose'], provision=True)
        logging.info('DummyHSM initialized.')
    else:
        logging.info('Initializing HSM...')
        hsm = HSM(verbose=config['verbose'])
        logging.info('HSM initialized.')

    # Create card object which connects and reconnects to inserted cards
    if config['devices']['card']['dummy']:
        logging.info('Initializing DummyCard...')
        card = DummyCard(verbose=config['verbose'], provision=True)
        logging.info('DummyCard initialized.')
    else:
        logging.info('Initializing Card...')
        card = Card(verbose=config['verbose'])
        logging.info('Card watcher initialized.')

    # Create ATM object with bank, hsm, and card instances
    logging.info('Initializing ATM...')
    atm = ATM(bank, hsm, card)
    logging.info('ATM initialized.')

    logging.info('Initializing Provision Tool...')
    provision_tool = ProvisionTool(bank, hsm, card)
    logging.info('Provision Tool initialized.')

    # Start xmlrpc server on host and port specified in config.yaml
    logging.info('Initializing ATM xmlrpc interface...')
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((config['devices']['atm']['host'], config['devices']['atm']['port']))

    # Register built-in rpc introspections
    server.register_introspection_functions()

    # Register api exposed by atm and hsm
    server.register_function(atm.hello)
    server.register_function(atm.withdraw)
    server.register_function(atm.check_balance)
    server.register_function(atm.change_pin)
    server.register_function(provision_tool.provision_card)
    server.register_function(provision_tool.provision_atm)

    logging.info('ATM xmlrpc interface initialized.')
    logging.info('ATM listening on %s:%s' % (config['devices']['atm']['host'], str(config['devices']['atm']['port'])))
    # Start xmlrpc server
    server.serve_forever()


if __name__ == '__main__':
    main()
