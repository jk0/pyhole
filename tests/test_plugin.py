# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from pyhole.core import plugin
from tests.conftest import FakeMessage, FakeSession


def _make_echo():
    class Echo(plugin.Plugin):
        """Echo plugin for tests."""

        @plugin.hook_add_command("echo")
        def echo(self, message, params=None, **kwargs):
            """Echo params back."""
            message.dispatch(params or "empty")

        @plugin.hook_add_keyword("bug")
        def keyword_bug(self, message, params=None, **kwargs):
            """Keyword hook."""
            message.dispatch(f"bug {params}")

    return Echo


def _load(session: FakeSession) -> None:
    _make_echo()
    plugin._reset_variables()
    plugin._init_plugins(session)


def test_command_with_prefix(clean_plugins) -> None:
    session = FakeSession()
    _load(session)
    message = FakeMessage(session, ".echo hello")
    plugin.poll_messages(session, message)
    assert message.dispatched == ["hello"]


def test_command_private_without_prefix(clean_plugins) -> None:
    session = FakeSession()
    _load(session)
    message = FakeMessage(session, "echo hello")
    plugin.poll_messages(session, message, private=True)
    assert "hello" in message.dispatched


def test_command_addressed_by_nick(clean_plugins) -> None:
    session = FakeSession()
    _load(session)
    message = FakeMessage(session, "pyhole: echo hi")
    plugin.poll_messages(session, message)
    assert "hi" in message.dispatched
    assert session.addressed is True


def test_unknown_command_is_ignored(clean_plugins) -> None:
    session = FakeSession()
    _load(session)
    message = FakeMessage(session, ".nope")
    plugin.poll_messages(session, message)
    assert message.dispatched == []


def test_keyword_hook(clean_plugins) -> None:
    session = FakeSession()
    _load(session)
    message = FakeMessage(session, "see bug123 for details")
    plugin.poll_messages(session, message)
    assert "bug 123" in message.dispatched


def test_active_commands(clean_plugins) -> None:
    session = FakeSession()
    _load(session)
    assert "echo" in plugin.active_commands()
    assert "bug" in plugin.active_keywords()
    assert "Echo" in plugin.active_plugins()
