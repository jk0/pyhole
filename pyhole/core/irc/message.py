#   Copyright 2011 Josh Kearney
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

'''Pyhole Message'''

import irc.client as irclib
from irc import connection

from .. import log


class Message(object):
    def __init__(self, source, target):
        self.log = log.get_logger()
        self.source = source
        self.target = target

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, _source):
        self._source = _source

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, _target):
        self._target = _target

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, _message):
        self._message = _message

    @property
    def reply(self):
        return self._reply

    @reply.setter
    def reply(self, _reply):
        self._reply = self._mangle_msg(_reply)

    def _mangle_msg(self, msg):
        """Prepare the message for sending."""
        if not hasattr(msg, "encode"):
            try:
                msg = str(msg)
            except Exception:
                self.log.error("msg cannot be converted to string")
                return

        msg = msg.split("\n")
        # NOTE(jk0): 10 is completely arbitrary for now.
        if len(msg) > 10:
            msg = msg[0:8]
            msg.append("...")

        return msg

    def dispatch(self):
        self.log.error("Message Dispatcher is not implemented")

    @classmethod
    def Factory(cls, _class, *args, **kwargs):
        types = {}
        for i in cls.__subclasses__():
            types[i.__name__] = i
        return types[_class](*args, **kwargs)

    @staticmethod
    def getMessage(**kwargs):
        return kwargs.pop("full_message")


class Notice(Message):
    def __init__(self, source, target):
        super(Notice, self).__init__(source, target)

    def dispatch(self, irc):
        """Dispatch message as notice."""
        for line in self.reply:
            irc.notice(self.target, line)
            if irclib.is_channel(self.target):
                self.log.info("-%s- <%s> %s" % (self.target, irc.nick, line))
            else:
                self.log.info("<%s> %s" % (irc.nick, line))


class Reply(Message):
    def __init__(self, source, target):
        super(Reply, self).__init__(source, target)

    def dispatch(self, irc):
        """dispatch message as a reply."""
        for line in self.reply:
            if irc.addressed:
                source = self.source.split("!")[0]
                irc.privmsg(self.target, "%s: %s" % (source, line))
                self.log.info("-%s- <%s> %s: %s" % (self.target, irc.nick,
                              source, line))
            else:
                irc.privmsg(self.target, line)
                if irclib.is_channel(self.target):
                    self.log.info("-%s- <%s> %s" % (self.target, irc.nick,
                                  line))
                else:
                    self.log.info("<%s> %s" % (irc.nick, line))
