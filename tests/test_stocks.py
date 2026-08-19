# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

from pyhole.plugins import stocks
from tests.conftest import FakeMessage, FakeSession, call_unwrapped


def test_stock_quote(monkeypatch, clean_plugins) -> None:
    payload = {
        "chart": {"result": [{"meta": {"regularMarketPrice": 12.5, "chartPreviousClose": 10.0}}]}
    }

    def fake_get(url, **kwargs):
        return SimpleNamespace(json=lambda: payload, status_code=200)

    monkeypatch.setattr("pyhole.plugins.stocks.request.get", fake_get)

    session = FakeSession()
    plugin_obj = stocks.Stocks(session)
    message = FakeMessage(session, ".stock aapl")
    call_unwrapped(plugin_obj.stocks, plugin_obj, message, "aapl")
    assert message.dispatched
    assert "AAPL: 12.5" in message.dispatched[0]
