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

"""Pyhole Search Plugin"""


import imdb
import re
import simplejson
import urllib

from xml.dom import minidom

from pyhole import utils


class Search(object):
    """Provide access to search engines"""

    def __init__(self, irc):
        self.irc = irc

    @utils.spawn
    def google(self, params=None):
        """Search Google (ex: .g <query>)"""
        if params:
            query = urllib.urlencode({"q": params})
            url = ("http://ajax.googleapis.com/ajax/"
                "services/search/web?v=1.0&%s" % query)

            try:
                response = urllib.urlopen(url)
            except IOError:
                self.irc.say("Unable to fetch Google data")
                return

            json = simplejson.loads(response.read())
            results = json["responseData"]["results"]
            if results:
                for r in results:
                    self.irc.say("%s: %s" % (
                        r["titleNoFormatting"].encode("ascii", "ignore"),
                        r["unescapedUrl"]))
            else:
                self.irc.say("No results found: '%s'" % params)
        else:
            self.irc.say(self.google.__doc__)

    def g(self, params=None):
        """Alias of google"""
        self.google(params)

    @utils.spawn
    def imdb(self, params=None):
        """Search IMDb (ex: .imdb <query>)"""
        if params:
            i = imdb.IMDb()

            try:
                results = i.search_movie(params, results=4)
            except IOError:
                self.irc.say("Unable to fetch IMDb data")
                return

            if results:
                for r in results:
                    self.irc.say("%s (%s): http://www.imdb.com/title/tt%s/" % (
                        r["title"],
                        r["year"],
                        r.movieID))
            else:
                self.irc.say("No results found: '%s'" % params)
        else:
            self.irc.say(self.imdb.__doc__)

    @utils.spawn
    def twitter(self, params=None):
        """Search Twitter (ex: .twitter <query>)"""
        if params:
            query = urllib.urlencode({"q": params, "rpp": 4})
            url = "http://search.twitter.com/search.json?%s" % query

            try:
                response = urllib.urlopen(url)
            except IOError:
                self.irc.say("Unable to fetch Twitter data")
                return

            json = simplejson.loads(response.read())
            results = json["results"]
            if results:
                for r in results:
                    self.irc.say("@%s: %s" % (
                        r["from_user"],
                        utils.decode_entities(
                            r["text"].encode("ascii", "ignore"))))
            else:
                self.irc.say("No results found: '%s'" % params)
        else:
            self.irc.say(self.twitter.__doc__)

    @utils.spawn
    def urban(self, params=None):
        """Search Urban Dictionary (ex: .urban <query>)"""
        if params:
            query = urllib.urlencode({"term": params})
            url = "http://www.urbandictionary.com/define.php?%s" % query

            try:
                response = urllib.urlopen(url)
            except IOError:
                self.irc.say("Unable to fetch Urban Dictionary data")
                return

            html = response.read()
            if re.search("<i>%s</i>\nisn't defined" % params, html):
                self.irc.say("No results found: '%s'" % params)
            else:
                r = (re.compile("<div class=\"definition\">(.*)</div>"
                    "<div class=\"example\">"))
                m = r.search(html)
                for i, line in enumerate(m.group(1).split("<br/>")):
                    if i <= 4:
                        line = utils.decode_entities(line)
                        self.irc.say(line)
                    else:
                        self.irc.say("[...] %s" % url)
                        break
        else:
            self.irc.say(self.urban.__doc__)

    @utils.spawn
    def wikipedia(self, params=None):
        """Search Wikipedia (ex: .wikipedia <query>)"""
        if params:
            query = urllib.urlencode({
                "action": "query",
                "generator": "allpages",
                "gaplimit": 4,
                "gapfrom": params,
                "format": "xml"})
            url = "http://en.wikipedia.org/w/api.php?%s" % query

            try:
                response = urllib.urlopen(url)
            except IOError:
                self.irc.say("Unable to fetch Wikipedia data")
                return

            xml = minidom.parseString(response.read())
            for i in xml.childNodes[0].childNodes[1].childNodes[0].childNodes:
                title = i._attrs["title"].firstChild.data
                title = re.sub(" ", "_", title)
                self.irc.say("http://en.wikipedia.org/wiki/%s" % title)
        else:
            self.irc.say(self.wikipedia.__doc__)

    @utils.spawn
    def youtube(self, params=None):
        """Search YouTube (ex: .youtube <query>)"""
        if params:
            query = urllib.urlencode({
                "q": params,
                "v": 2,
                "max-results": 4,
                "alt": "jsonc"})
            url = "http://gdata.youtube.com/feeds/api/videos?%s" % query

            try:
                response = urllib.urlopen(url)
            except IOError:
                self.irc.say("Unable to fetch YouTube data")
                return

            json = simplejson.loads(response.read())
            results = json["data"]
            if len(results) > 4:
                for r in results["items"]:
                    v = r["player"]["default"].split("&", 1)[0]
                    self.irc.say("%s: %s" % (r["title"], v))
            else:
                self.irc.say("No results found: '%s'" % params)
        else:
            self.irc.say(self.youtube.__doc__)
