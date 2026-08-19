# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

from pyhole.plugins import weather
from tests.conftest import FakeMessage, FakeSession, call_unwrapped


def test_weather_lookup(monkeypatch, clean_plugins) -> None:
    def fake_get(url, **kwargs):
        if "geocoding" in url:
            return SimpleNamespace(
                json=lambda: {
                    "results": [
                        {
                            "name": "Austin",
                            "admin1": "Texas",
                            "country_code": "US",
                            "latitude": 30.2,
                            "longitude": -97.7,
                        }
                    ]
                },
                status_code=200,
            )
        return SimpleNamespace(
            json=lambda: {"current_weather": {"temperature": 80.0, "windspeed": 5.0}},
            status_code=200,
        )

    monkeypatch.setattr("pyhole.plugins.weather.request.get", fake_get)
    session = FakeSession()
    plugin_obj = weather.Weather(session)
    message = FakeMessage(session, ".w Austin")
    call_unwrapped(plugin_obj.weather, plugin_obj, message, "Austin")
    assert message.dispatched
    assert "Austin" in message.dispatched[0]
    assert "80.0 F" in message.dispatched[0]


def test_weather_missing_location(clean_plugins) -> None:
    session = FakeSession()
    plugin_obj = weather.Weather(session)
    message = FakeMessage(session, ".w")
    call_unwrapped(plugin_obj.weather, plugin_obj, message, None)
    assert message.dispatched
    assert (
        "location" in message.dispatched[0].lower()
        or "Display current weather" in message.dispatched[0]
    )
