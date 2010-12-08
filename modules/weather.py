"""Pyhole Weather Module"""


import pywapi


class Weather(object):
    """Provide access to current weather data"""

    def __init__(self, irc):
        self.irc = irc

    def w(self, params=None):
        """Display current weather report (ex: .w <location>)"""
        if params:
            weather = pywapi.get_weather_from_google(params)

            if weather["current_conditions"]:
                city = weather["forecast_information"]["city"]
                temp_f = weather["current_conditions"]["temp_f"]
                temp_c = weather["current_conditions"]["temp_c"]
                humidity = weather["current_conditions"]["humidity"]
                wind = weather["current_conditions"]["wind_condition"]
                condition = weather["current_conditions"]["condition"]

                result = "%s: %sF/%sC   %s   %s   %s" % (
                    city,
                    temp_f,
                    temp_c,
                    humidity,
                    wind,
                    condition)
                self.irc.send_msg(result)
            else:
                self.irc.send_msg("'%s' not found." % params)
        else:
            self.irc.send_msg(self.w.__doc__)
