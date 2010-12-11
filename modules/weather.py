"""Pyhole Weather Module"""


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
            w = pywapi.get_weather_from_google(params)
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
