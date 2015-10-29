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

"""Network Process Class"""

import multiprocessing
import sys
import time

from pyhole.core import log
from pyhole.core import utils


LOG = log.get_logger()
CONFIG = utils.get_config()


class Process(multiprocessing.Process):
    """A network connection process."""
    def __init__(self, network):
        super(Process, self).__init__()
        self.network = network
        self.reconnect_delay = CONFIG.get("reconnect_delay", type="int")

    def run(self):
        """A network connection."""
        while True:
            try:
                network_config = utils.get_config(self.network)
                if network_config.get("api_token", default=None):
                    from pyhole.core.slack import client
                else:
                    from pyhole.core.irc import client

                connection = client.Client(self.network)
            except Exception, exc:
                LOG.exception(exc)
                LOG.error("Retrying in %d seconds" % self.reconnect_delay)

                time.sleep(self.reconnect_delay)

                continue

            try:
                connection.start()
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception, ex:
                LOG.exception(ex)
                LOG.error("Retrying in %d seconds" % self.reconnect_delay)

                time.sleep(self.reconnect_delay)

                continue
