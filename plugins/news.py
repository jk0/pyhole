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

"""Pyhole News Plugin"""

from xml.dom import minidom

from pyhole import plugin
from pyhole import utils


class News(plugin.Plugin):
    """Provide access to news feeds"""

    @plugin.hook_add_command("cnn")
    @utils.spawn
    def cnn(self, params=None, **kwargs):
        """Display current CNN news (ex: .cnn)"""
        url = "http://rss.cnn.com/rss/cnn_topstories.rss"
        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        xml = minidom.parseString(response.read())
        for i, item in enumerate(xml.childNodes[2].childNodes[0].childNodes):
            if i >= 21 and i <= 28 and item.childNodes:
                ref = item.childNodes
                self.irc.reply("%s: %s" % (ref[1].firstChild.data,
                        ref[5].firstChild.data))

    @plugin.hook_add_command("digg")
    @utils.spawn
    def digg(self, params=None, **kwargs):
        """Display current Digg news (ex: .digg)"""
        url = "http://services.digg.com/2.0/story.getTopNews?type=rss"
        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        xml = minidom.parseString(response.read())
        for i, item in enumerate(xml.childNodes[0].childNodes[1].childNodes):
            if i >= 15 and i <= 21 and item.childNodes:
                ref = item.childNodes
                self.irc.reply("%s: %s" % (ref[1].firstChild.data.strip(),
                        ref[3].firstChild.data.strip()))

    @plugin.hook_add_command("reddit")
    @utils.spawn
    def reddit(self, params=None, **kwargs):
        """Display current reddit news (ex: .reddit)"""
        url = "http://www.reddit.com/.rss"
        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        xml = minidom.parseString(response.read())
        for i, item in enumerate(xml.childNodes[0].childNodes[0].childNodes):
            if i >= 4 and i <= 7:
                ref = item.childNodes
                self.irc.reply("%s: %s" % (
                        ref[0].firstChild.data.encode("ascii", "ignore"),
                        ref[1].firstChild.data.encode("ascii", "ignore")))
