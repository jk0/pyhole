#   Copyright 2012 Matt Dietz
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

"""Pyhole Unit Converter Plugin"""

try:
    import json
except ImportError:
    import simplejson as json

import urllib

from pyhole import plugin
from pyhole import utils

class UnitConverter(plugin.Plugin):
    """Hit the Google API to convert units""" 

    @plugin.hook_add_command('convert')
    @utils.spawn
    def convert(self, params=None, **kwargs):
        query = urllib.urlencode({"q": params})
        url = ("http://www.google.com/ig/calculator?%s" % query)
        response = self.irc.fetch_url(url, self.name)
        if not response:
            self.irc.reply("Unit mismatch")
            return

        body = response.read()

        # the google calculator returns javascript style JSON
        rhs = body.split(',')[1]
        rhs = rhs.replace('"', '')
        self.irc.reply(rhs[5:])



