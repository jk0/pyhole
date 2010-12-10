#!/usr/bin/env python
"""pyhole - A modular IRC bot for Python developers."""


import logging
import time
import sys

from pyhole import config
from pyhole import irc


__version__ = "0.0.1"

conf = config.Config("pyhole.cfg", "pyhole")


def logger(name):
    """Log handler"""
    debug = conf.get("debug", "bool")
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(name)s:%(levelname)s] %(message)s")
    return logging.getLogger(name)


def main():
    """Main Loop"""
    log = logger("MAIN")
    reconnect_delay = conf.get("reconnect_delay", "int")

    while True:
        try:
            connection = irc.IRC(conf, logger("IRC"), __version__)
        except Exception as e:
            log.error(e)
            log.error("Retrying in %d seconds" % reconnect_delay)
            time.sleep(reconnect_delay)
            continue

        try:
            connection.start()
        except KeyboardInterrupt:
            log.info("Shutting down")
            sys.exit(0)


if __name__ == "__main__":
    main()
