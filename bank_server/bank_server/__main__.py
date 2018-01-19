"""
The main file for the bank_server package.
Initializes and runs bank server
"""

import os
import sys
import threading
import logging
from logging import handlers
import yaml
from . import Bank, AdminBackend


def main():
    """
        main:
            - load configuration yaml
            - initialize logging
            - create database mutex
            - start admin interface daemon thread
            - start bank interface
    """
    # Load configuartion from yaml
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

    logging.info('Config loaded and logging initialized')

    # Create db mutex for use by admin and bank backends
    db_mutex = threading.Lock()
    thread_obj = threading.Thread(target=AdminBackend, args=(config, db_mutex))
    thread_obj.daemon = True
    thread_obj.start()

    Bank(config, db_mutex)


if __name__ == "__main__":
    main()
