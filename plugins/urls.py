#   Copyright 2011 Josh Kearney
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

"""Pyhole URL Plugin"""

import re

from pyhole import plugin
from pyhole import utils


class Url(plugin.Plugin):
    """Provide access to URL data"""

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
        self.url = None

    @plugin.hook_add_command("title")
    @utils.spawn
    def title(self, params=None, **kwargs):
        """Display the title of the a URL (ex: .title <url>)"""
        if params:
            self._find_title(params.split(" ", 1)[0])
        else:
            if self.url:
                self._find_title(self.url)

    @plugin.hook_add_msg_regex("http:\/\/|www\.")
    def _watch_for_url(self, params=None, **kwargs):
        """Watch and keep track of the latest URL"""
        try:
            self.url = kwargs["full_message"].split(" ", 1)[0]
        except TypeError:
            return

    def _find_title(self, url):
        """Find the title of a given URL"""
        if not url.startswith("http://"):
            url = "http://" + url

        response = self.irc.fetch_url(url, self.name).read()
        response = re.sub("\n", "", response)
        response = re.sub("  +", "", response)

        r = re.compile("<title>(.*)</title>")
        m = r.search(response)

        if m:
            title = utils.decode_entities(m.group(1))
            self.irc.reply(title)
        else:
            self.irc.reply("No title found for %s" % url)
