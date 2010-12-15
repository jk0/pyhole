#   Copyright 2010 Josh Kearney
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

from pyhole import utils


class Weather(object):
    """Provide access to current weather data"""

    def __init__(self, irc):
        self.irc = irc

    @utils.spawn
    def weather(self, params=None):
        """Display current weather report (ex: .w <location>)"""
        if params:
            try:
                w = pywapi.get_weather_from_google(params)
            except Exception:
                self.irc.say("Unable to fetch weather data")
                return

            if w["current_conditions"]:
                city = w["forecast_information"]["city"]
                temp_f = w["current_conditions"]["temp_f"]
                temp_c = w["current_conditions"]["temp_c"]
                humidity = w["current_conditions"]["humidity"]
                wind = w["current_conditions"]["wind_condition"]
                condition = w["current_conditions"]["condition"]

                result = "%s: %sF/%sC   %s   %s   %s" % (
                    city,
                    temp_f,
                    temp_c,
                    humidity,
                    wind,
                    condition)
                self.irc.say(result)
            else:
                self.irc.say("Location not found: '%s'" % params)
        else:
            self.irc.say(self.weather.__doc__)

    def w(self, params=None):
        """Alias of weather"""
        self.weather(params)
