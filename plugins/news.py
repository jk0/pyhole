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


import urllib

from xml.dom import minidom

from pyhole import utils


class News(object):
    """Provide access to news feeds"""

    def __init__(self, irc):
        self.irc = irc

    @utils.spawn
    def cnn(self, params=None):
        """Display current CNN news (ex: .cnn)"""
        url = "http://rss.cnn.com/rss/cnn_topstories.rss"

        try:
            response = urllib.urlopen(url)
        except IOError:
            self.irc.say("Unable to fetch CNN data")
            return

        xml = minidom.parseString(response.read())
        for i, item in enumerate(xml.childNodes[2].childNodes[0].childNodes):
            if i >= 21 and i <= 28 and item.childNodes:
                ref = item.childNodes
                self.irc.say("%s: %s" % (
                    ref[1].firstChild.data,
                    ref[5].firstChild.data))

    @utils.spawn
    def digg(self, params=None):
        """Display current Digg news (ex: .digg)"""
        url = "http://services.digg.com/2.0/story.getTopNews?type=rss"

        try:
            response = urllib.urlopen(url)
        except IOError:
            self.irc.say("Unable to fetch Digg data")
            return

        xml = minidom.parseString(response.read())
        for i, item in enumerate(xml.childNodes[0].childNodes[1].childNodes):
            if i >= 15 and i <= 21 and item.childNodes:
                ref = item.childNodes
                self.irc.say("%s: %s" % (
                    ref[1].firstChild.data.strip(),
                    ref[3].firstChild.data.strip()))

    @utils.spawn
    def hackernews(self, params=None):
        """Display current Hacker News links (ex: .hackernews)"""
        url = "http://news.ycombinator.com/rss"

        try:
            response = urllib.urlopen(url)
        except IOError:
            self.irc.say("Unable to fetch Hacker News data")
            return

        xml = minidom.parseString(response.read())
        for i, item in enumerate(xml.firstChild.childNodes[0].childNodes):
            if i >= 3 and i <= 6:
                ref = item.childNodes
                self.irc.say("%s: %s" % (
                    ref[0].firstChild.data.strip(),
                    ref[1].firstChild.data))

    @utils.spawn
    def reddit(self, params=None):
        """Display current reddit news (ex: .reddit)"""
        url = "http://www.reddit.com/.rss"

        try:
            response = urllib.urlopen(url)
        except IOError:
            self.irc.say("Unable to fetch reddit data")
            return

        xml = minidom.parseString(response.read())
        for i, item in enumerate(xml.childNodes[0].childNodes[0].childNodes):
            if i >= 4 and i <= 7:
                ref = item.childNodes
                self.irc.say("%s: %s" % (
                    ref[0].firstChild.data.encode("ascii", "ignore"),
                    ref[1].firstChild.data.encode("ascii", "ignore")))

    @utils.spawn
    def slashdot(self, params=None):
        """Display current Slashdot news (ex: .slashdot)"""
        url = "http://rss.slashdot.org/Slashdot/slashdot"

        try:
            response = urllib.urlopen(url)
        except IOError:
            self.irc.say("Unable to fetch Slashdot data")
            return

        xml = minidom.parseString(response.read())
        for i, item in enumerate(xml.childNodes[1].childNodes[0].childNodes):
            if i >= 21 and i <= 24:
                ref = item.childNodes
                self.irc.say("%s: %s" % (
                    ref[0].firstChild.data,
                    ref[1].firstChild.data))
