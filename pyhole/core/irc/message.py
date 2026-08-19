# Copyright 2013-2026 Philip Schwartz, Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""IRC message wrappers."""

from __future__ import annotations

from typing import Any

import irc.client as irclib


class Message:
    def __init__(self, session: Any, message: str) -> None:
        self.session = session
        self.message = message

    def _mangle_msg(self, msg: Any) -> list[str]:
        if not hasattr(msg, "encode"):
            try:
                msg = str(msg)
            except Exception:
                self.session.log.error("msg cannot be converted to string")
                return []
        lines = str(msg).split("\n")
        if len(lines) > 10:
            lines = [*lines[:8], "..."]
        return lines

    def dispatch(self, reply: Any) -> None:
        raise NotImplementedError("Message Dispatcher is not implemented")

    @staticmethod
    def getMessage(**kwargs: Any) -> Any:
        return kwargs.pop("full_message")


class Notice(Message):
    def __init__(self, session: Any, message: str, target: str) -> None:
        super().__init__(session, message)
        self.target = target

    def dispatch(self, reply: Any) -> None:
        for line in self._mangle_msg(reply):
            self.session.notice(self.target, line)
            if irclib.is_channel(self.target):
                self.session.log.info("-%s- <%s> %s", self.target, self.session.nick, line)
            else:
                self.session.log.info("<%s> %s", self.session.nick, line)


class Reply(Message):
    def __init__(self, session: Any, message: str, source: str, target: str) -> None:
        super().__init__(session, message)
        self.source = source
        self.target = target

    def dispatch(self, reply: Any) -> None:
        for line in self._mangle_msg(reply):
            if self.session.addressed:
                source = self.source.split("!")[0]
                self.session.reply(self.target, f"{source}: {line}")
                self.session.log.info(
                    "-%s- <%s> %s: %s", self.target, self.session.nick, source, line
                )
            else:
                self.session.reply(self.target, line)
                if irclib.is_channel(self.target):
                    self.session.log.info("-%s- <%s> %s", self.target, self.session.nick, line)
                else:
                    self.session.log.info("<%s> %s", self.session.nick, line)
