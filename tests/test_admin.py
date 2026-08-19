# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from pyhole.plugins import admin
from tests.conftest import FakeMessage, FakeSession


def test_help_lists_commands(clean_plugins) -> None:
    session = FakeSession()
    plugin_obj = admin.Admin(session)
    message = FakeMessage(session, ".help")
    plugin_obj.help(message)
    assert any("Learn how to use plugins" in line for line in message.dispatched)


def test_version(clean_plugins) -> None:
    session = FakeSession()
    plugin_obj = admin.Admin(session)
    message = FakeMessage(session, ".version")
    plugin_obj.version(message)
    assert session.version in message.dispatched


def test_say_requires_admin(clean_plugins) -> None:
    session = FakeSession()
    plugin_obj = admin.Admin(session)
    message = FakeMessage(session, ".say #chan hi", source="eve!ident")
    plugin_obj.say(message, "#chan hi")
    assert message.dispatched == ["Sorry, you are not authorized to do that."]


def test_say_as_admin(clean_plugins) -> None:
    session = FakeSession()
    plugin_obj = admin.Admin(session)
    message = FakeMessage(session, ".say #chan hi", source="alice!ident")
    plugin_obj.say(message, "#chan hi")
    assert session.replies == [("#chan", "hi")]
