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

"""Pyhole Network Connections"""

import multiprocessing

from pyhole.core import utils


class Process(multiprocessing.Process):
    """A network connection."""
    def __init__(self, network):
        super(Process, self).__init__()
        self.network = network

    def run(self):
        """Run the network connection."""
        network_config = utils.get_config(self.network)
        if network_config.get("api_token", default=None):
            from pyhole.core.slack import client
        else:
            from pyhole.core.irc import client

        connection = client.Client(self.network)
        connection.start()
