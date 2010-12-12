#   Copyright 2010 Josh Kearney
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

"""Pyhole Entertainment Module"""


import re
import urllib

from pyhole import utils


class Entertainment(object):
    """Provide access to entertaining sites"""

    def __init__(self, irc):
        self.irc = irc

    @utils.spawn
    def grouphug(self, params=None):
        """Display a random Group Hug (ex: .grouphug)"""
        url = "http://grouphug.us/random"
        response = urllib.urlopen(url)
        html = response.read()
        r = re.compile("<div class=\"content\">\n    <p>(.*)</p>\n  </div>")
        m = r.search(html)
        if m:
            line = m.group(1)
            line = re.sub("<.*>", "", line)
            line = re.sub("&#8217;", "'", line)
            line = re.sub("&nbsp;", " ", line)
            line = re.sub("&#8230;", "...", line)
            line = re.sub("&#8220;", "\"", line)
            line = re.sub("&#8221;", "\"", line)
            line = re.sub("&#8212;", "-", line)
            self.irc.say(line)
        else:
            self.irc.say("Unable to parse GH data")

    @utils.spawn
    def lastnight(self, params=None):
        """Display a random Text From Last Night (ex: .lastnight)"""
        url = "http://www.textsfromlastnight.com/" \
            "Random-Texts-From-Last-Night.html"
        response = urllib.urlopen(url)
        html = response.read()
        r = re.compile("<p><a href=\"/Text-Replies-.+.html\">(.*)</a></p>")
        m = r.search(html)
        if m:
            self.irc.say(m.group(1))
        else:
            self.irc.say("Unable to parse TFLN data")
