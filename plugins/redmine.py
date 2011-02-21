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

"""Pyhole Redmine Plugin"""

import urllib

from xml.dom import minidom

from pyhole import utils


class Redmine(object):
    """Provide access to the Redmine API"""

    def __init__(self, irc):
        self.irc = irc

    @utils.spawn
    def keyword_rm(self, params=None):
        """Retrieve Redmine bug information (ex: RM12345)"""
        if params:
            try:
                int(params)
            except ValueError:
                return

            url = "https://%s:password@%s/issues/%s.xml" % (
                self.irc.redmine_key,
                self.irc.redmine_domain,
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
                self.irc.redmine_domain,
                issue["id"]))
