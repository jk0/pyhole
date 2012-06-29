#   Copyright 2012 Josh Kearney
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

"""Pyhole Calculator Plugin"""

import urllib

from pyhole import plugin
from pyhole import utils


class Calculator(plugin.Plugin):
    """Provide access to Google's calculator"""

    @plugin.hook_add_command("calc")
    @utils.spawn
    def calc(self, params=None, **kwargs):
        """Use Google's calculator (ex: .c <expression>)"""
        if params:
            query = urllib.urlencode({"q": params})
            url = "http://www.google.com/ig/calculator?hl=en&%s" % query
            response = self.irc.fetch_url(url, self.name)
            if not response:
                return

            json = response.read()
            results = [i.replace("\"", "") for i in json[1:-1].split(",")]

            expression = None
            answer = None

            for result in results:
                result = result.split(": ")
                if result[0] == "lhs":
                    expression = result[1]
                elif result[0] == "rhs":
                    answer = result[1]

            if expression and answer:
                self.irc.reply("%s is %s" % (expression, answer))
            else:
                self.irc.reply("Unable to calculate '%s'" % params)
        else:
            self.irc.reply(self.calc.__doc__)

    @plugin.hook_add_command("c")
    def alias_c(self, params=None, **kwargs):
        """Alias of calc"""
        self.calc(params, **kwargs)
