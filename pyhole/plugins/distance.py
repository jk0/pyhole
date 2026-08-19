# Copyright 2015-2026 Rick Harris and contributors
# SPDX-License-Identifier: Apache-2.0

"""Distance between two users or locations via Google Maps."""

from __future__ import annotations

from pyhole.core import plugin, request, utils


class Distance(plugin.Plugin):
    """Driving distance between two users or places."""

    @plugin.hook_add_command("distance")
    @utils.require_params
    @utils.spawn
    def distance(self, message, params=None, **kwargs):
        """Display distances (ex: .distance <nick|loc> [to <nick|loc>])."""
        maps = utils.get_config("GoogleMaps")
        key = maps.get("key", default="")
        if not key:
            message.dispatch("No Google Maps API key set.")
            return

        parts = params.split(" to ")
        dest_nick = parts[0].strip()
        origin_nick = parts[1].strip() if len(parts) > 1 else message.source.split("!")[0]

        dest = _lookup_saved_location(dest_nick) or dest_nick
        origin = _lookup_saved_location(origin_nick) or origin_nick

        try:
            resp = request.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                params={"origin": origin, "destination": dest, "key": key},
            )
            msg = resp.json()["routes"][0]["legs"][0]["distance"]["text"]
        except Exception:
            msg = "Unable to fetch data from Google Maps."
        message.dispatch(msg)


def _lookup_saved_location(nick: str) -> str | None:
    for directory in ("Weather", "Wunderground"):
        try:
            names = utils.list_files(directory)
        except OSError:
            continue
        for filename in names:
            if filename.split("!")[0] == nick:
                return utils.read_file(directory, filename)
    return None
