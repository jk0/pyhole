"""Pyhole Weather Module"""


import memcache
import pywapi


class Weather(object):
    """Provide access to current weather data"""

    def __init__(self, irc):
        self.irc = irc

    def weather(self, params=None):
        """Display current weather report (ex: .w <location>)"""
        if params:
            mc = memcache.Client(["127.0.0.1:11211"])
            weather = mc.get(params)

            if weather:
                self.irc.log.debug("Fetching cached weather (%s)" % params)
                self.irc.send_msg(weather)
            else:
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
                    self.irc.send_msg(result)

                    self.irc.log.debug("Caching weather data (%s)" % params)
                    mc.set(params, result, 600)
                else:
                    self.irc.send_msg("'%s' not found." % params)
        else:
            self.irc.send_msg(self.weather.__doc__)

    def w(self, params=None):
        """Alias of weather"""
        self.weather(params)
