# Copyright 2015-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Slack message wrappers."""

from __future__ import annotations

from typing import Any


class Message:
    def __init__(self, session: Any, message: str) -> None:
        self.session = session
        self.message = message

    def dispatch(self, reply: Any) -> None:
        raise NotImplementedError("Message Dispatcher is not implemented")

    @staticmethod
    def getMessage(**kwargs: Any) -> Any:
        return kwargs.pop("full_message")


class Reply(Message):
    def __init__(self, session: Any, message: str, source: str, target: str) -> None:
        super().__init__(session, message)
        self.source = source
        self.target = target

    def dispatch(self, msg: Any) -> None:
        text = str(msg)
        if self.session.addressed:
            self.session.reply(self.target, f"{self.source}: {text}")
            self.session.log.info(
                "-#%s- <%s> %s: %s", self.target, self.session.nick, self.source, text
            )
        else:
            self.session.reply(self.target, text)
            self.session.log.info("-#%s- <%s> %s", self.target, self.session.nick, text)
