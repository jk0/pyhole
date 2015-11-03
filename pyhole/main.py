#   Copyright 2010-2015 Josh Kearney
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

"""pyhole - A modular IRC & Slack bot for Python developers."""

import sys
import time

from pyhole.core import log
from pyhole.core import process
from pyhole.core import utils
from pyhole.core import version


LOG = log.get_logger()
CONFIG = utils.get_config()


def Main():
    """Main IRC loop."""
    networks = CONFIG.get("networks", type="list")
    log.setup_logger()
    LOG.info("Starting %s" % version.version_string())
    LOG.info("Connecting to networks: %s" % ", ".join(networks))

    procs = []
    for network in networks:
        proc = process.Process(network)
        proc.start()
        procs.append(proc)

    try:
        while True:
            time.sleep(1)
            for proc in procs:
                if not proc.is_alive():
                    procs.remove(proc)

            if not procs:
                LOG.info("No longer connected to any networks, shutting down")
                sys.exit(0)
    except KeyboardInterrupt:
        LOG.info("Caught KeyboardInterrupt, shutting down")
