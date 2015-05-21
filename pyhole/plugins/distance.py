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

        parts = params.split(' ')
        if not parts:
            message.dispatch(self.distance.__doc__)
            return

        dest_nick = parts[0]

        if len(parts) > 1:
            origin_nick = parts[1]
        else:
            origin_nick = message.source.split('!')[0]

        dest_zip = None
        origin_zip = None
        for filename in utils.list_files('Weather'):
            nick, ident = filename.split('!')
            if nick == dest_nick:
                dest_zip = utils.read_file('Weather', filename)
            if nick == origin_nick:
                origin_zip = utils.read_file('Weather', filename)

        if not dest_zip:
            message.dispatch("No location set for '%s' yet"
                             " (use: .w set <zip>)" % dest_nick)
            return

        if not origin_zip:
            message.dispatch("No location set for '%s' yet"
                             " (use: .w set <zip>)" % origin_nick)
            return

        resp =  requests.get('https://maps.googleapis.com/maps/api'
                             '/directions/json?origin=%s&destination=%s'
                             '&key=%s' % (origin_zip, dest_zip, key))
        if resp.status_code == 200:
            msg = resp.json()['routes'][0]['legs'][0]['distance']['text']
        else:
            msg = "Unable to fetch data from Google Maps"

        message.dispatch(msg)

    @plugin.hook_add_command("dist")
    def alias_dist(self, message, params=None, **kwargs):
        """Alias of distance"""
        self.distance(message, params, **kwargs)
