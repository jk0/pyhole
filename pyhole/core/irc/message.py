#   Copyright 2013 Philip Schwartz
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

"""Pyhole Message"""

import irc.client as irclib


class Message(object):
    def __init__(self, session, message):
        self.session = session
        self.message = message

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, _message):
        self._message = _message

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, _session):
        self._session = _session

    def _mangle_msg(self, msg):
        """Prepare the message for sending."""
        if not hasattr(msg, "encode"):
            try:
                msg = str(msg)
            except Exception:
                self.session.log.error("msg cannot be converted to string")
                return

        msg = msg.split("\n")
        # NOTE(jk0): 10 is completely arbitrary for now.
        if len(msg) > 10:
            msg = msg[0:8]
            msg.append("...")

        return msg

    def dispatch(self, reply):
        raise NotImplementedError("Message Dispatcher is not implemented")

    @staticmethod
    def getMessage(**kwargs):
        return kwargs.pop("full_message")


class Notice(Message):
    def __init__(self, session, message, target):
        super(Notice, self).__init__(session, message)
        self.target = target

    def dispatch(self, reply):
        """Dispatch message as notice."""
        _reply = self._mangle_msg(reply)
        for line in _reply:
            self.session.notice(self.target, line)
            if irclib.is_channel(self.target):
                self.session.log.info("-%s- <%s> %s" % (self.target,
                                                        self.session.nick,
                                                        line))
            else:
                self.session.log.info("<%s> %s" % (self.session.nick, line))


class Reply(Message):
    def __init__(self, session, message, source, target):
        super(Reply, self).__init__(session, message)
        self.source = source
        self.target = target

    def dispatch(self, reply):
        """dispatch message as a reply."""
        _reply = self._mangle_msg(reply)
        for line in _reply:
            if self.session.addressed:
                source = self.source.split("!")[0]
                self.session.privmsg(self.target, "%s: %s" % (source, line))
                self.session.log.info("-%s- <%s> %s: %s" % (self.target,
                                                            self.session.nick,
                                                            source, line))
            else:
                self.session.privmsg(self.target, line)
                if irclib.is_channel(self.target):
                    self.session.log.info("-%s- <%s> %s" % (self.target,
                                                            self.session.nick,
                                                            line))
                else:
                    self.session.log.info("<%s> %s" % (self.session.nick,
                                                       line))
