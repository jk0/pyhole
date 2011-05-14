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

"""Pyhole Entertainment Plugin"""

import re

from pyhole import plugin
from pyhole import utils


class Entertainment(plugin.Plugin):
    """Provide access to entertaining sites"""

    def __init__(self, irc, conf_file):
        self.irc = irc
        self.name = self.__class__.__name__

    @plugin.hook_add_command("grouphug")
    @utils.spawn
    def grouphug(self, params=None, **kwargs):
        """Display a random Group Hug (ex: .grouphug)"""
        url = "http://grouphug.us/random"
        response = self.irc.fetch_url(url, self.name)

        html = response.read()
        r = re.compile("<div class=\"content\">\n\s+<p>(.*)</p>\n\s+</div>")
        m = r.search(html)
        if m:
            line = utils.decode_entities(m.group(1))
            self.irc.reply(line)
        else:
            self.irc.reply("Unable to parse Group Hug data")

    @plugin.hook_add_command("lastnight")
    @utils.spawn
    def lastnight(self, params=None, **kwargs):
        """Display a random Text From Last Night (ex: .lastnight)"""
        url = ("http://www.textsfromlastnight.com/"
               "Random-Texts-From-Last-Night.html")

        response = self.irc.fetch_url(url, self.name)

        html = response.read()
        r = re.compile("<p><a href=\"/Text-Replies-.+.html\">(.*)</a></p>")
        m = r.search(html)
        if m:
            self.irc.reply(m.group(1))
        else:
            self.irc.reply("Unable to parse Texts From Last Night data")
