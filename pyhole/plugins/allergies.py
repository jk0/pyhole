#   Copyright 2015-2016 Jason Meridth
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


from pyhole.core import plugin
from pyhole.core import request
from pyhole.core import utils


class Allergies(plugin.Plugin):
    """Provide access to current allergy data."""

    @plugin.hook_add_command("allergies")
    @utils.spawn
    def allergies(self, message, params=None, **kwargs):
        """Display current allergies in San Antonio, TX (ex: .allergies)."""
        url = "http://txallergy.info/api/allergy/today"

        response = request.get(url)
        if response.status_code != 200:
            return

        text = "Allergies for today: "
        for a in response.json():
            text = text + "%s - %s (%s) | " % (a["allergen"], a["level"],
                                               a["count"])
        text = text.rstrip(" ")
        text = text.rstrip("|")

        message.dispatch(text)

    @plugin.hook_add_command("pollen")
    def alias_pollen(self, message, params=None, **kwargs):
        """Alias of allergies."""
        self.allergies(message, params, **kwargs)
