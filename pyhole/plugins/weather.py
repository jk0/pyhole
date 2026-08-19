# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Weather plugin backed by the free Open-Meteo API (no key required)."""

from __future__ import annotations

from pyhole.core import plugin, request, utils

_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST = "https://api.open-meteo.com/v1/forecast"


class Weather(plugin.Plugin):
    """Current weather via Open-Meteo."""

    @plugin.hook_add_command("weather")
    @utils.spawn
    def weather(self, message, params=None, **kwargs):
        """Display current weather (ex: .w [set] [<location>])."""
        if params:
            location = params
            if location.startswith("set "):
                location = location[4:]
                utils.write_file(self.name, message.source, location)
                message.dispatch("Location information saved.")
        else:
            location = utils.read_file(self.name, message.source)
            if not location:
                message.dispatch(self.weather.__doc__)
                return

        try:
            geo = request.get(_GEOCODE, params={"name": location, "count": 1})
            results = geo.json().get("results") or []
            if not results:
                message.dispatch(f"Location not found: '{location}'")
                return
            place = results[0]
            forecast = request.get(
                _FORECAST,
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current_weather": True,
                    "windspeed_unit": "mph",
                    "temperature_unit": "fahrenheit",
                },
            )
            current = forecast.json().get("current_weather") or {}
        except Exception:
            message.dispatch("Unable to fetch weather data.")
            return

        if not current:
            message.dispatch(f"Location not found: '{location}'")
            return

        name = place.get("name", location)
        admin = place.get("admin1") or ""
        country = place.get("country_code") or ""
        where = ", ".join(part for part in (name, admin, country) if part)
        temp = current.get("temperature")
        wind = current.get("windspeed")
        message.dispatch(f"{where}: {temp} F   Wind: {wind} mph")

    @plugin.hook_add_command("w")
    def alias_w(self, message, params=None, **kwargs):
        """Alias of weather."""
        self.weather(message, params, **kwargs)
