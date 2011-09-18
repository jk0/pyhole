#   Copyright 2010-2011 Josh Kearney
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

import pywapi

from pyhole import plugin
from pyhole import utils


class Weather(plugin.Plugin):
    """Provide access to current weather data"""

    @plugin.hook_add_command("weather")
    @utils.spawn
    def weather(self, params=None, **kwargs):
        """Display current weather report (ex: .w [set] [<location>])"""
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
            w = pywapi.get_weather_from_google(location)
        except Exception:
            self.irc.reply("Unable to fetch weather data")
            return

        if w["current_conditions"]:
            city = w["forecast_information"]["city"]
            temp_f = w["current_conditions"]["temp_f"]
            temp_c = w["current_conditions"]["temp_c"]
            humidity = w["current_conditions"]["humidity"]
            wind = w["current_conditions"]["wind_condition"]
            condition = w["current_conditions"]["condition"]

            result = "%s: %sF/%sC   %s   %s   %s" % (city, temp_f, temp_c,
                    humidity, wind, condition)
            self.irc.reply(result)
        else:
            self.irc.reply("Location not found: '%s'" % location)

    @plugin.hook_add_command("w")
    def alias_w(self, params=None, **kwargs):
        """Alias of weather"""
        self.weather(params, **kwargs)
