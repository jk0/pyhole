# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

from pyhole.plugins import urls
from tests.conftest import FakeMessage, FakeSession, call_unwrapped


def test_find_title(monkeypatch, clean_plugins) -> None:
    html = b"<html><head><title>Hello &amp; World</title></head></html>"
    monkeypatch.setattr(
        "pyhole.plugins.urls.request.get",
        lambda url, **kwargs: SimpleNamespace(
            content=html, headers={"Content-Type": "text/html"}, status_code=200
        ),
    )
    session = FakeSession()
    plugin_obj = urls.Url(session)
    message = FakeMessage(session, ".title https://example.com")
    call_unwrapped(plugin_obj._find_title, plugin_obj, message, "https://example.com")
    assert message.dispatched
    assert "Hello & World" in message.dispatched[0]


def test_matches_host() -> None:
    assert urls._matches_host("https://www.youtube.com/watch?v=abc")
    assert urls._matches_host("https://youtu.be/abc")
    assert not urls._matches_host("https://example.com/")
