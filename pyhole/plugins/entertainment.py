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

from BeautifulSoup import BeautifulSoup

from pyhole import plugin
from pyhole import utils


class Entertainment(plugin.Plugin):
    """Provide access to entertaining sites"""

    @plugin.hook_add_command("grouphug")
    @utils.spawn
    def grouphug(self, params=None, **kwargs):
        """Display a random Group Hug (ex: .grouphug)"""
        url = "http://grouphug.us/random"
        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        soup = BeautifulSoup(response.read())
        grouphug = utils.decode_entities(
                soup.findAll(id=re.compile("node-\d+"))[2].p.contents[0])
        self.irc.reply(grouphug)

    @plugin.hook_add_command("lastnight")
    @utils.spawn
    def lastnight(self, params=None, **kwargs):
        """Display a random Text From Last Night (ex: .lastnight)"""
        url = ("http://www.textsfromlastnight.com/"
                "Random-Texts-From-Last-Night.html")
        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        soup = BeautifulSoup(response.read())
        lastnight = utils.decode_entities(
                soup.findAll(href=re.compile(
                        "/Text-Replies-\d+.html"))[0].contents[0])
        self.irc.reply(lastnight)
