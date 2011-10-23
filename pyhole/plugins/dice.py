#   Copyright 2011 John Dickinson
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

"""Pyhole Dice Plugin"""

import random

from pyhole import plugin


class Dice(plugin.Plugin):
    """Provide access to dice games"""

    @plugin.hook_add_command("roll")
    def roll(self, params=None, **kwargs):
        """Roll dice (ex: .roll 2d6)"""
        if params:
            query = params.split()[0]
            try:
                if "d" not in query:
                    count = 1
                    sides = int(query)
                elif query.startswith("d"):
                    count = 1
                    sides = int(query[1:])
                else:
                    count, sides = query.split("d")
                    count = int(count)
                    sides = int(sides)
            except (TypeError, ValueError):
                result = self.roll.__doc__
            else:
                result = 0
                for _ in xrange(count):
                    result += random.randint(1, sides)
        else:
            result = self.roll.__doc__

        self.irc.reply(result)
