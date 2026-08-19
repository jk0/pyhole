# Copyright 2015-2026 Jason Meridth and contributors
# SPDX-License-Identifier: Apache-2.0

"""Allergy plugin."""

from __future__ import annotations

from pyhole.core import plugin, request, utils


class Allergies(plugin.Plugin):
    """Current allergy data for San Antonio, TX."""

    @plugin.hook_add_command("allergies")
    @utils.spawn
    def allergies(self, message, params=None, **kwargs):
        """Display current allergies in San Antonio, TX (ex: .allergies)."""
        try:
            response = request.get("http://txallergy.info/api/allergy/today")
            data = response.json()
        except Exception:
            return
        if response.status_code != 200 or not isinstance(data, list):
            return
        parts = [f"{row['allergen']} - {row['level']} ({row['count']})" for row in data]
        message.dispatch("Allergies for today: " + " | ".join(parts))

    @plugin.hook_add_command("pollen")
    def alias_pollen(self, message, params=None, **kwargs):
        """Alias of allergies."""
        self.allergies(message, params, **kwargs)
