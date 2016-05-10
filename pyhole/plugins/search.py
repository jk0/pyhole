#   Copyright 2010-2016 Josh Kearney
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

import json
import re

from BeautifulSoup import BeautifulSoup

from pyhole.core import plugin
from pyhole.core import utils


class Search(plugin.Plugin):
    """Provide access to search engines."""

    @plugin.hook_add_command("urban")
    @utils.require_params
    @utils.spawn
    def urban(self, message, params=None, **kwargs):
        """Search Urban Dictionary (ex: .urban <query>)."""
        url = "http://www.urbandictionary.com/define.php"
        response = utils.fetch_url(url, params={"term": params})
        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.content)

        try:
            meaning = soup.find("div", {"class": "meaning"}).text
            example = soup.find("div", {"class": "example"}).text
        except AttributeError:
            message.dispatch("No results found: '%s'" % params)

        meaning = utils.decode_entities(meaning)
        example = utils.decode_entities(example)

        message.dispatch("%s (ex: %s)" % (meaning, example))

    @plugin.hook_add_command("wikipedia")
    @utils.require_params
    @utils.spawn
    def wikipedia(self, message, params=None, **kwargs):
        """Search Wikipedia (ex: .wikipedia <query>)."""
        url = "https://en.wikipedia.org/w/api.php"
        response = utils.fetch_url(url, params={
            "action": "query",
            "generator": "allpages",
            "gaplimit": 4,
            "gapfrom": params,
            "format": "json"
        })

        if response.status_code != 200:
            return

        pages = json.loads(response.content)["query"]["pages"]
        for page in pages.values():
            title = page["title"]
            title = re.sub(" ", "_", title)
            message.dispatch("http://en.wikipedia.org/wiki/%s" % title)
