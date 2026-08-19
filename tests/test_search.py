# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

from pyhole.plugins import search
from tests.conftest import FakeMessage, FakeSession, call_unwrapped


def test_wikipedia(monkeypatch, clean_plugins) -> None:
    monkeypatch.setattr(
        "pyhole.plugins.search.request.get",
        lambda url, **kwargs: SimpleNamespace(
            json=lambda: ["python", ["Python"], [""], ["https://en.wikipedia.org/wiki/Python"]],
            status_code=200,
        ),
    )
    session = FakeSession()
    plugin_obj = search.Search(session)
    message = FakeMessage(session, ".wikipedia python")
    call_unwrapped(plugin_obj.wikipedia, plugin_obj, message, "python")
    assert message.dispatched == ["https://en.wikipedia.org/wiki/Python"]


def test_urban(monkeypatch, clean_plugins) -> None:
    monkeypatch.setattr(
        "pyhole.plugins.search.request.get",
        lambda url, **kwargs: SimpleNamespace(
            json=lambda: {"list": [{"definition": "a test", "example": "this is a test"}]},
            status_code=200,
        ),
    )
    session = FakeSession()
    plugin_obj = search.Search(session)
    message = FakeMessage(session, ".urban test")
    call_unwrapped(plugin_obj.urban, plugin_obj, message, "test")
    assert "a test" in message.dispatched[0]
