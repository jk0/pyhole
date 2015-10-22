#   Copyright 2015 Josh Kearney
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

"""Slack Message Class"""

from pyhole.core import log


class Message(object):
    def __init__(self, client, message):
        self.log = log.get_logger()
        self.client = client
        self.message = message

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, _message):
        self._message = _message

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, _client):
        self._client = _client

    def dispatch(self, reply):
        self.log.error("Message Dispatcher is not implemented")

    @staticmethod
    def getMessage(**kwargs):
        return kwargs.pop("full_message")


class Reply(Message):
    def __init__(self, client, message, source, target):
        super(Reply, self).__init__(client, message)
        self.source = source
        self.target = target

    def dispatch(self, msg):
        """Dispatch message as a reply."""
        if self.client.addressed:
            self.client.reply(self.target, "%s: %s" % (self.source, msg))
            self.log.info("-%s- <%s> %s: %s" % (self.target, self.client.nick,
                          self.source, msg))
        else:
            self.client.reply(self.target, msg)
            self.log.info("-%s- <%s> %s" % (self.target, self.client.nick,
                                            msg))
