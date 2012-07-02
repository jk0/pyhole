#   Copyright 2010-2012 Josh Kearney
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

"""Pyhole Weather Plugin"""

import pywunderground

from pyhole import plugin
from pyhole import utils


class Weather(plugin.Plugin):
    """Provide access to current weather data"""

    @plugin.hook_add_command("weather")
    @utils.spawn
    def weather(self, params=None, **kwargs):
        """Display current weather report (ex: .w [set] [<location>])"""
        wunderground = utils.get_config("Wunderground")
        api_key = wunderground.get("key")

        if params:
            location = params
            if location.startswith("set "):
                location = location[4:]
                utils.write_file(self.name, self.irc.source, location)
                self.irc.reply("Location information saved")
        else:
            location = utils.read_file(self.name, self.irc.source)
            if not location:
                self.irc.reply(self.weather.__doc__)
                return

        try:
            w = pywunderground.request(api_key, ["conditions"], location)
        except Exception:
            self.irc.reply("Unable to fetch weather data")
            return

        if w.get("current_observation"):
            w = w["current_observation"]

            city = w["display_location"]["full"]
            zip_code = w["display_location"]["zip"]
            temp = w["temperature_string"]
            heat_index = "%s F (%s C)" % (w["heat_index_f"], w["heat_index_c"])
            humidity = w["relative_humidity"]
            wind = w["wind_string"]
            condition = w["weather"]

            zip_code = "" if zip_code == "00000" else " %s" % zip_code
            humidity = "N/A%" if len(humidity) > 3 else humidity

            result = ("%s%s: [%s / Feels Like: %s]   Humidity: %s   "
                    "Wind: %s   %s") % (city, zip_code, temp, heat_index,
                    humidity, wind, condition)

            self.irc.reply(result)
        else:
            self.irc.reply("Location not found: '%s'" % location)

    @plugin.hook_add_command("w")
    def alias_w(self, params=None, **kwargs):
        """Alias of weather"""
        self.weather(params, **kwargs)
