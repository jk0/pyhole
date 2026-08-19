# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole message queue."""

from __future__ import annotations

import multiprocessing
import time
from typing import Any

from pyhole.core import utils

QUEUE: multiprocessing.Queue = multiprocessing.Queue()


class MessageQueue:
    """Cross-network message queue.

    Items are ``(network, target, message)`` tuples. Each network process
    watches the queue and only delivers items intended for itself.
    """

    def __init__(self) -> None:
        self.queue = QUEUE

    def put(self, item: tuple[str, str, str]) -> None:
        self.queue.put_nowait(item)

    @utils.spawn
    def watch(self, session: Any) -> None:
        while True:
            item = self.queue.get()
            actual_network = session.log.name
            intended_network = item[0]
            if actual_network != intended_network:
                self.queue.put(item)
                time.sleep(0.05)
                continue
            session.reply(item[1], item[2])
