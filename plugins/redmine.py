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
        """Redmine bugs for a user (ex: .rbugs <login>)"""
        if params:
            login = params.split(" ", 1)[0]
            user_id = self._find_user(login)

            issues = self._find_issues(user_id)
            for i, issue in enumerate(issues):
                if i <= 4:
                    self._find_issue(issue["id"])
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
            utils.ensure_int(params)
            self._find_issue(params)

    def _find_issues(self, user_id):
        """Find all issues for a Redmine user"""
        url = "%s/issues.json?assigned_to_id=%s" % (
            self.redmine_url,
            user_id)

        try:
            response = urllib.urlopen(url)
        except IOError:
            self.irc.say("Unable to fetch Redmine data")
            return

        return simplejson.loads(response.read())["issues"]

    def _find_user(self, login):
        """Find a specific Redmine user"""
        for user in self._find_users():
            if login == user["login"]:
                return user["id"]
        else:
            self.irc.say("Redmine user '%s' not found" % login)
            return

    def _find_users(self):
        """Find all Redmine users"""
        url = "%s/users.json?limit=1000" % self.redmine_url

        try:
            response = urllib.urlopen(url)
        except IOError:
            self.irc.say("Unable to fetch Redmine data")
            return

        return simplejson.loads(response.read())["users"]

    def _find_issue(self, issue_id):
        """Find and display a Redmine issue"""
        url = "%s/issues/%s.json" % (self.redmine_url, issue_id)

        try:
            response = urllib.urlopen(url)
        except IOError:
            self.irc.say("Unable to fetch Redmine data")
            return

        try:
            issue = simplejson.loads(response.read())["issue"]
        except:
            return

        self.irc.say("Redmine bug #%s: %s [Status: %s, Assignee: %s]" % (
            issue["id"],
            issue["subject"],
            issue["status"]["name"],
            issue["assigned_to"]["name"]))
        self.irc.say("https://%s/issues/show/%s" % (
            self.irc.redmine_domain,
            issue["id"]))
