#!/usr/bin/env python
"""
pyhole - A simple, yet modular IRC bot written in Python.
"""


import logging
import time

from pyhole import config
from pyhole import irc 


conf = config.Config("pyhole.cfg", "pyhole")

def logger(name):
    """Log handler

    Args:
        name
    """
    debug = conf.get("debug", "bool")
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(name)s:%(levelname)s] %(message)s"
    )
    return logging.getLogger(name)

def main():
    """Main Loop"""
    log = logger("MAIN")

    while True:
        try:
            connection = irc.IRC(conf, logger("IRC"))
        except Exception, e:
            log.error(e)
            log.info("Unable to connect -- trying again in 60 seconds")
            time.sleep(60)
            continue

        try:
            while True:
                connection.ircobj.process_once()
        except Exception, e:
            log.error(e)
            pass

        time.sleep(30)


if __name__ == "__main__":
    main()
