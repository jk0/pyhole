#!/usr/bin/env python
"""pyhole - A modular IRC bot for Python developers."""


import logging
import time

from multiprocessing import Process

from pyhole import config
from pyhole import irc


__version__ = "0.0.1"
__config__ = "pyhole.cfg"

b_config = config.Config(__config__, "pyhole")


def logger(name):
    """Log handler"""
    debug = b_config.get("debug", "bool")
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


def irc_process(b_log, b_config, network):
    """IRC network connection process"""
    n_config = config.Config(__config__, network)
    n_log = logger(network)
    reconnect_delay = b_config.get("reconnect_delay", "int")

    while True:
        try:
            connection = irc.IRC(b_config, n_config, n_log, __version__)
        except Exception as e:
            b_log.error(e)
            b_log.error("Retrying in %d seconds" % reconnect_delay)
            time.sleep(reconnect_delay)

        connection.start()


def main():
    """Main Loop"""
    b_log = logger("MAIN")
    networks = network_list(b_config.sections())

    for network in networks:
        p = Process(target=irc_process, args=(b_log, b_config, network))
        p.start()
        time.sleep(1)


if __name__ == "__main__":
    main()
