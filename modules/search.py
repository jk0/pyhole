"""Pyhole Search Module"""


import simplejson
import time
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
            for result in results:
                self.irc.say("%s: %s" % (
                    result["titleNoFormatting"].encode("ascii", "ignore"),
                    result["unescapedUrl"]))
                time.sleep(.10)
        else:
            self.irc.say(self.google.__doc__)

    def g(self, params=None):
        """Alias of google"""
        self.google(params)

    def imdb(self, params=None):
        """Search IMDb (ex: .imdb <query>)"""
        pass

    def twitter(self, params=None):
        """Search Twitter (ex: .twitter <query>)"""
        pass

    def urban(self, params=None):
        """Search Urban Dictionary (ex: .urban <query>)"""
        pass

    def youtube(self, params=None):
        """Search YouTube (ex: .youtube <query>)"""
        pass
