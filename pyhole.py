#!/usr/bin/env python

#   Copyright 2010-2011 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""pyhole - A modular IRC bot for Python developers."""

import multiprocessing
import sys
import time

from pyhole import config
from pyhole import irc
from pyhole import utils


__VERSION__ = "pyhole v0.5.2 - http://pyhole.org"
__CONFIG__ = "pyhole.cfg"

CONFIG = config.Config(__CONFIG__, "Pyhole")
DEBUG = CONFIG.get("debug", "bool")


def network_list(sections):
    """Prepare the list of IRC networks"""
    networks = []
    for network in sections:
        if network != "Pyhole" and network != "Redmine":
            networks.append(network)
    return networks


def irc_connection(network):
    """IRC network connection"""
    network_info = config.Config(__CONFIG__, network)
    log = utils.logger(network, DEBUG)
    reconnect_delay = CONFIG.get("reconnect_delay", "int")

    while True:
        try:
            connection = irc.IRC(CONFIG, network_info, log, __VERSION__)
        except Exception, e:
            log.error(e)
            log.error("Retrying in %d seconds" % reconnect_delay)
            time.sleep(reconnect_delay)
            continue

        try:
            connection.start()
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception, e:
            log.error(e)
            log.error("Retrying in %d seconds" % reconnect_delay)
            time.sleep(reconnect_delay)
            continue


if __name__ == "__main__":
    LOG = utils.logger("MAIN", DEBUG)
    NETWORKS = network_list(CONFIG.sections())

    LOG.info("Connecting to IRC Networks: %s" % ", ".join(NETWORKS))
    for network in NETWORKS:
        p = multiprocessing.Process(target=irc_connection, args=(network,))
        p.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOG.info("Caught KeyboardInterrupt, shutting down")
