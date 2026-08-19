# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Back-compat alias: Weather Underground's API is gone; this loads Weather."""

from pyhole.plugins.weather import Weather as Wunderground

__all__ = ["Wunderground"]
