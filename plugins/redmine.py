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
import simplejson

from xml.dom import minidom

from pyhole import utils


class Redmine(object):
    """Provide access to the Redmine API"""

    def __init__(self, irc):
        self.irc = irc
        self.redmine_url = "https://%s:password@%s" % (
            self.irc.redmine_key,
            self.irc.redmine_domain)

    @utils.spawn
    def rbugs(self, params=None):
        """Redmine bugs for a user (ex: .rbugs <user>)"""
        if params:
            user = params.split(" ", 1)[0]
            user_id = None
            users_url = "%s/users.json?limit=1000" % self.redmine_url

            try:
                users_response = urllib.urlopen(users_url)
            except IOError:
                self.irc.say("Unable to fetch Redmine data")
                return

            users = simplejson.loads(users_response.read())["users"]
            for redmine_user in users:
                if user == redmine_user["login"]:
                    user_id = int(redmine_user["id"])

            if not user_id:
                self.irc.say("Redmine user '%s' not found" % user)
                return

            issues_url = "%s/issues.json?assigned_to_id=%d" % (
                self.redmine_url,
                user_id)

            try:
                issues_response = urllib.urlopen(issues_url)
            except IOError:
                self.irc.say("Unable to fetch Redmine data")
                return

            issues = simplejson.loads(issues_response.read())["issues"]
            for i, issue in enumerate(issues):
                if i <= 4:
                    self.irc.say("Redmine bug #%d: %s"
                        "[Status: %s, Assignee: %s]" % (
                            issue["id"],
                            issue["subject"],
                            issue["status"]["name"],
                            issue["assigned_to"]["name"]))
                    self.irc.say("https://%s/issues/show/%s" % (
                        self.irc.redmine_domain,
                        issue["id"]))
                else:
                    self.irc.say("[...] truncated last %d bugs" % (
                        len(issues) - i))
                    return
        else:
            self.irc.say(self.rbugs.__doc__)

    @utils.spawn
    def keyword_rm(self, params=None):
        """Retrieve Redmine bug information (ex: RM12345)"""
        if params:
            try:
                int(params)
            except ValueError:
                return

            url = "%s/issues/%s.xml" % (self.redmine_url, params)

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

            self.irc.say("Redmine bug #%s: %s [Status: %s, Assignee: %s]" % (
                issue["id"],
                issue["subject"],
                issue["status"],
                issue["assigned_to"]))
            self.irc.say("https://%s/issues/show/%s" % (
                self.irc.redmine_domain,
                issue["id"]))
