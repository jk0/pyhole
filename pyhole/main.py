#   Copyright 2010-2016 Josh Kearney
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

"""pyhole - A modular IRC & Slack bot."""

import time

from pyhole.core import api
from pyhole.core import logger
from pyhole.core import process
from pyhole.core import utils
from pyhole.core import version


def Main():
    """Main loop."""
    config = utils.get_config()
    log = logger.get_logger()
    networks = config.get("networks", type="list")

    log.info("Starting %s..." % version.version_string())
    log.info("Connecting to networks: %s" % ", ".join(networks))

    procs = []
    for network in networks:
        proc = process.Process(network)
        proc.start()
        procs.append(proc)

    try:
        if config.get("api_enabled", type="bool"):
            api.run()

        while True:
            time.sleep(1)
            for proc in procs:
                if not proc.is_alive():
                    procs.remove(proc)

            if not procs:
                log.info("No longer connected to any networks; shutting down.")
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        for proc in procs:
            proc.terminate()
