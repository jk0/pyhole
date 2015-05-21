#   Copyright 2015 Rick Harris
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
import shlex

import requests

from pyhole.core import plugin, utils


class Distance(plugin.Plugin):
    """Display distance between two IRC users (using their Weather Zip Code)"""

    @plugin.hook_add_command("distance")
    @utils.spawn
    def distance(self, message, params=None, **kwargs):
        """Display distance between users (ex: .dist <nick> [<nick>])"""
        maps_api = utils.get_config("Googlemaps")
        try:
            key = maps_api.get("key")
        except Exception:
            message.dispatch("No Google Maps API key set")
            return

        parts = shlex.split(params)
        if not parts:
            message.dispatch(self.distance.__doc__)
            return

        dest_nick = parts[0].strip()

        if len(parts) > 1:
            origin_nick = parts[1].strip()
        else:
            origin_nick = message.source.split('!')[0]

        dest = None
        origin = None
        for filename in utils.list_files('Weather'):
            nick, ident = filename.split('!')
            if nick == dest_nick:
                dest = utils.read_file('Weather', filename)
            if nick == origin_nick:
                origin = utils.read_file('Weather', filename)

        if not dest:
            # They passed in a location
            dest = dest_nick

        if not origin:
            # They passed in a location
            origin = origin_nick

        resp =  requests.get('https://maps.googleapis.com/maps/api'
                             '/directions/json?origin=%s&destination=%s'
                             '&key=%s' % (origin, dest, key))

        msg = None
        if resp.status_code == 200:
            try:
                msg = resp.json()['routes'][0]['legs'][0]['distance']['text']
            except IndexError:
                pass

        if not msg:
            msg = "Unable to fetch data from Google Maps"

        message.dispatch(msg)

    @plugin.hook_add_command("dist")
    def alias_dist(self, message, params=None, **kwargs):
        """Alias of distance"""
        self.distance(message, params, **kwargs)
