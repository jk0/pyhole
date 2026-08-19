# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole network connections."""

from __future__ import annotations

import multiprocessing

from pyhole.core import utils


class Process(multiprocessing.Process):
    """A network connection running in its own process."""

    def __init__(self, network: str) -> None:
        super().__init__(name=network)
        self.network = network

    def run(self) -> None:
        network_config = utils.get_config(self.network)
        if network_config.get("api_token", default=None):
            from pyhole.core.slack import client
        else:
            from pyhole.core.irc import client

        connection = client.Client(self.network)
        connection.start()
