"""Pyhole Search Module"""


import imdb
import simplejson
import urllib


class Search(object):
    """Provide access to search engines"""

    def __init__(self, irc):
        self.irc = irc

    def google(self, params=None):
        """Search Google (ex: .g <query>)"""
        if params:
            query = urllib.urlencode({"q": params})
            url = "http://ajax.googleapis.com/ajax/" \
                "services/search/web?v=1.0&%s" % query
            response = urllib.urlopen(url)
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

    def imdb(self, params=None):
        """Search IMDb (ex: .imdb <query>)"""
        if params:
            i = imdb.IMDb()
            results = i.search_movie(params, results=4)
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

    def twitter(self, params=None):
        """Search Twitter (ex: .twitter <query>)"""
        if params:
            query = urllib.urlencode({"q": params, "rpp": 4})
            url = "http://search.twitter.com/search.json?%s" % query
            response = urllib.urlopen(url)
            json = simplejson.loads(response.read())
            results = json["results"]
            if results:
                for r in results:
                    self.irc.say("@%s: %s" % (
                        r["from_user"],
                        r["text"].encode("ascii", "ignore")))
            else:
                self.irc.say("No results found: '%s'" % params)
        else:
            self.irc.say(self.twitter.__doc__)

    def urban(self, params=None):
        """Search Urban Dictionary (ex: .urban <query>)"""
        pass

    def youtube(self, params=None):
        """Search YouTube (ex: .youtube <query>)"""
        if params:
            query = urllib.urlencode({
                "q": params,
                "v": 2,
                "max-results": 4,
                "alt": "jsonc"})
            url = "http://gdata.youtube.com/feeds/api/videos?%s" % query
            response = urllib.urlopen(url)
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
