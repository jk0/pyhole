#   Copyright 2016 Josh Kearney
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

"""Pyhole Message Queue"""

import multiprocessing

import utils


QUEUE = multiprocessing.Queue()


class FIFOQueue(object):
    """Global message queue."""

    def __init__(self):
        self.queue = QUEUE

    def put(self, item):
        """Place an item in the queue."""
        self.queue.put_nowait(item)

    @utils.spawn
    def watch(self, session):
        """Watch the queue for incoming messages."""
        while True:
            network, source, target, message = self.queue.get()

            # NOTE(jk0): Right now there is no way to guarantee that the
            # message will get delivered to the right network.
            _msg = "New message from %s: %s" % (source, message)
            session.reply(target, _msg)
