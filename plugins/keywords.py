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

"""Pyhole Keyword Plugin"""

import urllib

from launchpadlib.launchpad import Launchpad as LP
from xml.dom import minidom

from pyhole import utils


class Keywords(object):
    """Watch for keywords in IRC messages"""

    def __init__(self, irc):
        self.irc = irc
        self.launchpad = LP.login_anonymously(
            "pyhole",
            "production",
            self.irc.cache)

    @utils.spawn
    def keyword_lp(self, params=None):
        """Retrieve Launchpad bug information (ex: LP12345)"""
        if params:
            try:
                int(params)
            except ValueError:
                return

            lp = "https://bugs.launchpad.net/launchpad/+bug/"

            try:
                bug = self.launchpad.bugs[params]

                self.irc.say("Launchpad bug #%s: %s [Status: %s]" % (
                    bug.id,
                    bug.title,
                    bug.bug_tasks[len(bug.bug_tasks) - 1].status))
                self.irc.say("%s%s" % (lp, bug.id))
            except Exception:
                return

    @utils.spawn
    def keyword_rm(self, params=None):
        """Retrieve Redmine bug information (ex: RM12345)"""
        if params:
            try:
                int(params)
            except ValueError:
                return

            key = "abcd1234"
            domain = "redmine.example.com"
            url = "https://%s:password@%s/issues/%s.xml" % (
                key,
                domain,
                params)

            try:
                response = urllib.urlopen(url)
            except IOError:
                self.irc.say("Unable to fetch Redmine data")
                return

            xml = minidom.parseString(response.read())
            for item in xml.childNodes:
                issue = dict(
                    id=item.childNodes[0].firstChild.data,
                    status=item.childNodes[3].\
                        _attrsNS.values()[1].firstChild.data,
                    assigned_to=item.childNodes[6].\
                        _attrsNS.values()[1].firstChild.data,
                    subject=item.childNodes[9].firstChild.data)

            self.irc.say("Redmine bug #%s: %s [Status: %s, Assigned: %s]" % (
                issue["id"],
                issue["subject"],
                issue["status"],
                issue["assigned_to"]))
            self.irc.say("https://%s/issues/show/%s" % (
                domain,
                issue["id"]))
