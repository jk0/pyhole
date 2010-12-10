#!/usr/bin/env python
"""pyhole - A modular IRC bot for Python developers."""


import logging
import time
import sys

from pyhole import config
from pyhole import irc


__version__ = "0.0.1"
__config__ = "pyhole.cfg"

bot = config.Config(__config__, "pyhole")


def logger(name):
    """Log handler"""
    debug = bot.get("debug", "bool")
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(name)s:%(levelname)s] %(message)s")
    return logging.getLogger(name)


def network_list(sections):
    """Prepare the list of IRC networks"""
    networks = []
    for network in sections:
        if network != "pyhole":
            networks.append(network)
    return networks


def main():
    """Main Loop"""
    log = logger("MAIN")
    networks = network_list(bot.sections())
    reconnect_delay = bot.get("reconnect_delay", "int")

    while True:
        for network in networks:
            try:
                connection = irc.IRC(
                    bot,
                    config.Config(__config__, network),
                    logger(network),
                    __version__)

                try:
                    connection.start()
                except KeyboardInterrupt:
                    sys.exit(0)
            except Exception as e:
                log.error(e)
                log.error("Retrying in %d seconds" % reconnect_delay)
                time.sleep(reconnect_delay)


if __name__ == "__main__":
    main()
