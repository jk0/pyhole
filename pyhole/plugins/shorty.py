#   Copyright 2010-2011 Josh Kearney
#   Copyright 2012 Aaron Lee
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

"""Pyhole VersionOne Plugin"""

import urllib

from pyhole import plugin
from pyhole import utils

class Shorty(plugin.Plugin):
    """Provides a short url when a long one is posted.
       talks to https://github.com/wwkeyboard/extrashortyshortshorturl"""

    def __init__(self, irc):
        self.irc = irc
        self.shorty = utils.get_config("Shorty")
        self.create_url = self.shorty.get('create_url')
        self.name = self.__class__.__name__

    @plugin.hook_add_keyword("http://")
    def http(self, params=None, **kwargs):
        print params
        if len(params) > 20:
            data = urllib.urlencode({'url':params})
            print "shortying %s" % data
            self.irc.reply(urllib.urlopen(self.create_url,
                                          data).read())
