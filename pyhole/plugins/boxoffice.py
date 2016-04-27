#   Copyright 2015-2016 Rick Harris
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

"""Pyhole Box Office Plugin"""

from BeautifulSoup import BeautifulSoup

from pyhole.core import plugin
from pyhole.core import utils


class Boxoffice(plugin.Plugin):
    """Display top box office movies."""

    @plugin.hook_add_command("boxoffice")
    @utils.spawn
    def boxoffice(self, message, params=None, **kwargs):
        """Display top box office movies"""
        resp = utils.fetch_url("http://www.rottentomatoes.com")
        if resp.status_code != 200:
            message.dispatch("Could not fetch box office results.")
            return

        message.dispatch("Top 10 at the Box Office")
        message.dispatch("=" * 64)
        soup = BeautifulSoup(resp.text)
        rows = soup.findAll("table", id="Top-Box-Office")[0].findAll("tr")
        for row in rows:
            children = row.findAll("td")
            try:
                score = row("span", **{"class": "tMeterScore"})[0].contents[0]
                title = children[1].find("a").string
                take = children[2].string.strip()
            except Exception:
                pass
            msg = "%s %s%s" % (score.rjust(3), title.ljust(40), take.rjust(10))
            message.dispatch(msg)
