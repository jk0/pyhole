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

try:
    import json
except ImportError:
    import simplejson as json

import re
import urllib

from BeautifulSoup import BeautifulSoup
from xml.dom import minidom

from pyhole import plugin
from pyhole import utils


class Search(plugin.Plugin):
    """Provide access to search engines"""

    @plugin.hook_add_command("google")
    @utils.spawn
    def google(self, params=None, **kwargs):
        """Search Google (ex: .g <query>)"""
        if params:
            query = urllib.urlencode({"q": params})
            url = ("http://ajax.googleapis.com/ajax/"
                    "services/search/web?v=1.0&%s" % query)
            response = self.irc.fetch_url(url, self.name)
            if not response:
                return

            json_obj = json.loads(response.read())
            results = json_obj["responseData"]["results"]
            if results:
                for r in results:
                    self.irc.reply("%s: %s" % (
                            r["titleNoFormatting"].encode("ascii", "ignore"),
                            r["unescapedUrl"]))
            else:
                self.irc.reply("No results found: '%s'" % params)
        else:
            self.irc.reply(self.google.__doc__)

    @plugin.hook_add_command("g")
    def alias_g(self, params=None, **kwargs):
        """Alias of google"""
        self.google(params, **kwargs)

    @plugin.hook_add_command("imdb")
    @utils.spawn
    def imdb(self, params=None, **kwargs):
        """Search IMDb (ex: .imdb <query>)"""
        if params:
            query = urllib.urlencode({"q": params})
            url = "http://www.imdb.com/find?s=all&%s" % query
            response = self.irc.fetch_url(url, self.name)
            if not response:
                return

            soup = BeautifulSoup(response.read())
            results = soup.findAll("td", {"valign": "top"})

            i = 0
            for result in results:
                if len(result) > 3 and len(result.contents[2].attrs) > 0:
                    id = result.contents[2].attrs[0][1]
                    title = utils.decode_entities(
                            result.contents[2].contents[0])
                    year = result.contents[2].nextSibling.strip()[0:6]

                    if not title.startswith("aka") and len(year):
                        self.irc.reply("%s %s: http://www.imdb.com%s" % (
                                title, year, id))
                        i += 1
                elif i >= 4:
                    break

            if i == 0:
                self.irc.reply("No results found: '%s'" % params)
        else:
            self.irc.reply(self.imdb.__doc__)

    @plugin.hook_add_command("twitter")
    @utils.spawn
    def twitter(self, params=None, **kwargs):
        """Search Twitter (ex: .twitter <query>)"""
        if params:
            query = urllib.urlencode({"q": params, "rpp": 4})
            url = "http://search.twitter.com/search.json?%s" % query
            response = self.irc.fetch_url(url, self.name)
            if not response:
                return

            json_obj = json.loads(response.read())
            results = json_obj["results"]
            if results:
                for r in results:
                    self.irc.reply("@%s: %s" % (r["from_user"],
                            utils.decode_entities(
                                    r["text"].encode("ascii", "ignore"))))
            else:
                self.irc.reply("No results found: '%s'" % params)
        else:
            self.irc.reply(self.twitter.__doc__)

    @plugin.hook_add_command("urban")
    @utils.spawn
    def urban(self, params=None, **kwargs):
        """Search Urban Dictionary (ex: .urban <query>)"""
        if params:
            query = urllib.urlencode({"term": params})
            url = "http://www.urbandictionary.com/define.php?%s" % query
            response = self.irc.fetch_url(url, self.name)
            if not response:
                return

            soup = BeautifulSoup(response.read())
            results = soup.findAll("div", {"class": "definition"})

            urban = ""
            if len(results):
                urban = " ".join(str(x) for x in soup.findAll(
                        "div", {"class": "definition"})[0].contents)

            if len(urban) > 0:
                for i, line in enumerate(urban.split("<br/>")):
                    if i <= 4:
                        self.irc.reply(utils.decode_entities(line))
                    else:
                        self.irc.reply("[...] %s" % url)
                        break
            else:
                self.irc.reply("No results found: '%s'" % params)
        else:
            self.irc.reply(self.urban.__doc__)

    @plugin.hook_add_command("wikipedia")
    @utils.spawn
    def wikipedia(self, params=None, **kwargs):
        """Search Wikipedia (ex: .wikipedia <query>)"""
        if params:
            query = urllib.urlencode({"action": "query",
                    "generator": "allpages", "gaplimit": 4,
                    "gapfrom": params, "format": "xml"})
            url = "http://en.wikipedia.org/w/api.php?%s" % query
            response = self.irc.fetch_url(url, self.name)
            if not response:
                return

            xml = minidom.parseString(response.read())
            for i in xml.childNodes[0].childNodes[1].childNodes[0].childNodes:
                title = i._attrs["title"].firstChild.data
                title = re.sub(" ", "_", title)
                self.irc.reply("http://en.wikipedia.org/wiki/%s" % title)
        else:
            self.irc.reply(self.wikipedia.__doc__)

    @plugin.hook_add_command("youtube")
    @utils.spawn
    def youtube(self, params=None, **kwargs):
        """Search YouTube (ex: .youtube <query>)"""
        if params:
            query = urllib.urlencode({"q": params, "v": 2, "max-results": 4,
                    "alt": "jsonc"})
            url = "http://gdata.youtube.com/feeds/api/videos?%s" % query
            response = self.irc.fetch_url(url, self.name)
            if not response:
                return

            json_obj = json.loads(response.read())
            results = json_obj["data"]
            if len(results) > 4:
                for r in results["items"]:
                    v = r["player"]["default"].split("&", 1)[0]
                    self.irc.reply("%s: %s" % (r["title"], v))
            else:
                self.irc.reply("No results found: '%s'" % params)
        else:
            self.irc.reply(self.youtube.__doc__)
