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
import optparse
import sys
import time

from pyhole import config
from pyhole import irc
from pyhole import utils


__VERSION__ = "pyhole v0.5.3 - http://pyhole.org"


def network_list(sections):
    """Prepare the list of IRC networks"""
    return [net for net in sections if net not in ["Pyhole", "Redmine"]]


def irc_connection(irc_network, conf):
    """IRC network connection"""
    network_info = config.Config(conf, irc_network)
    log = utils.logger(irc_network, LOG_DIR, DEBUG)
    reconnect_delay = CONFIG.get("reconnect_delay", "int")

    while True:
        try:
            connection = irc.IRC(CONFIG, network_info, log, __VERSION__, conf)
        except Exception, e:
            log.error(e)
            log.error("Retrying in %d seconds" % reconnect_delay)
            time.sleep(reconnect_delay)
            continue

        try:
            connection.start()
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception, e:
            log.error(e)
            log.error("Retrying in %d seconds" % reconnect_delay)
            time.sleep(reconnect_delay)
            continue


if __name__ == "__main__":
    PARSER = optparse.OptionParser(version=__VERSION__)
    PARSER.add_option("-c", "--config", dest="config", default="pyhole.cfg")
    PARSER.add_option("--debug", action="store_true", dest="debug")
    OPTIONS, ARGS = PARSER.parse_args()
    CONF = OPTIONS.config

    CONFIG = config.Config(CONF, "Pyhole")
    DEBUG = OPTIONS.debug or CONFIG.get("debug", "bool")
    LOG_DIR = CONFIG.get("log_dir")
    LOG = utils.logger("MAIN", LOG_DIR, DEBUG)
    NETWORKS = network_list(CONFIG.sections())

    LOG.info("Starting %s" % __VERSION__)
    LOG.info("Connecting to IRC Networks: %s" % ", ".join(NETWORKS))
    for network in NETWORKS:
        p = multiprocessing.Process(target=irc_connection,
                args=(network, CONF))
        p.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOG.info("Caught KeyboardInterrupt, shutting down")
