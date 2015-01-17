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

"""Pyhole Allergies Plugin"""

import datetime
import requests

from pyhole.core import plugin, utils


class Allergies(plugin.Plugin):
    """Provide access to current allergy data"""

    @plugin.hook_add_command("allergies")
    @utils.spawn
    def allergies(self, message, params=None, **kwargs):
        """Display current allergies in San Antonio, TX (ex: .allergies)

        original code:
        https://github.com/kremlinkev/Supybot-Pollen/blob/master/plugin.py
        """
        d = datetime.datetime.now()
        weekend = d.isoweekday() in (6, 7)
        if weekend:
            message.dispatch("Unable to fetch allergy data on weekends")
            return

        today = d.strftime("%Y-%m-%d")
        URL = "http://saallergy.info/day/%s" % today
        HEADERS = {"accept": "application/json"}

        try:
            r = requests.get(URL, headers=HEADERS)
        except Exception:
            message.dispatch("Unable to fetch allergy data")
            return

        data = r.json()
        text = "Allergies for %s: " % today
        for a in data["results"]:
            text = text + "%s - %s (%s) | " % (a["allergen"], a["level"],
                                               a["count"])
        text = text.rstrip(" ")
        text = text.rstrip("|")

        message.dispatch(text)
