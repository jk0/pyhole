#   Copyright 2015-2016 Rick Harris
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Pyhole Distance to User Plugin"""

import pywunderground

from pyhole.core import plugin
from pyhole.core import utils


class Distance(plugin.Plugin):
    """Display distance between two users by using their weather data."""

    @plugin.hook_add_command("distance")
    @utils.require_params
    @utils.spawn
    def distance(self, message, params=None, **kwargs):
        """Display distances (ex: .dist <nick|loc> [to <nick|loc>])."""
        maps_api = utils.get_config("GoogleMaps")
        try:
            key = maps_api.get("key")
        except Exception:
            message.dispatch("No Google Maps API key set.")
            return

        parts = params.split(" to ")
        if not parts:
            message.dispatch(self.distance.__doc__)
            return

        dest_nick = parts[0].strip()

        if len(parts) > 1:
            origin_nick = parts[1].strip()
        else:
            origin_nick = message.source.split("!")[0]

        dest = None
        origin = None
        for filename in utils.list_files("Wunderground"):
            nick = filename.split("!")[0]
            if nick == dest_nick:
                dest = utils.read_file("Wunderground", filename)
            if nick == origin_nick:
                origin = utils.read_file("Wunderground", filename)

        if not dest:
            # They passed in a location
            dest = dest_nick

        if not origin:
            # They passed in a location
            origin = origin_nick

        origin = _resolve_pws(origin)
        dest = _resolve_pws(dest)

        resp = utils.fetch_url("https://maps.googleapis.com/maps/api"
                               "/directions/json?origin=%s&destination=%s"
                               "&key=%s" % (origin, dest, key))

        msg = None
        if resp.status_code == 200:
            try:
                msg = resp.json()["routes"][0]["legs"][0]["distance"]["text"]
            except IndexError:
                pass

        if not msg:
            msg = "Unable to fetch data from Google Maps."

        message.dispatch(msg)


def _resolve_pws(location):
    """Look up the location of a PWS."""
    if location.lower().startswith("pws:"):
        wunderground = utils.get_config("Wunderground")
        api_key = wunderground.get("key")

        w = pywunderground.request(api_key, ["conditions"], location)

        return w["current_observation"]["display_location"]["zip"]

    return location
