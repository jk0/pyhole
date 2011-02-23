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

import simplejson

from pyhole import utils


class Redmine(object):
    """Provide access to the Redmine API"""

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
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
            i = 0
            for i, issue in enumerate(issues):
                if i <= 4:
                    self._find_issue(issue["id"])
                else:
                    self.irc.say("[...] truncated last %d bugs" % (
                        len(issues) - i))
                    break
            else:
                if i <= 0:
                    self.irc.say("No Redmine bugs found for '%s'" % login)
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

        response = self.irc.fetch_url(url, self.name)

        return simplejson.loads(response.read())["issues"]

    def _find_user(self, login):
        """Find a specific Redmine user"""
        for user in self._find_users():
            if login == user["login"]:
                return user["id"]

        for user in self._find_users(100):
            if login == user["login"]:
                return user["id"]

    def _find_users(self, offset=None):
        """Find all Redmine users"""
        if offset:
            url = "%s/users.json?limit=100&offset=%d" % (
                self.redmine_url,
                offset)
        else:
            url = "%s/users.json?limit=100" % self.redmine_url

        response = self.irc.fetch_url(url, self.name)

        return simplejson.loads(response.read())["users"]

    def _find_issue(self, issue_id):
        """Find and display a Redmine issue"""
        url = "%s/issues/%s.json" % (self.redmine_url, issue_id)
        response = self.irc.fetch_url(url, self.name)

        try:
            issue = simplejson.loads(response.read())["issue"]
        except:
            return

        self.irc.say("RM Bug #%s: %s [Status: %s, Assignee: %s]" % (
            issue["id"],
            issue["subject"],
            issue["status"]["name"],
            issue.get("assigned_to", {}).get("name", "N/A")))
        self.irc.say("https://%s/issues/show/%s" % (
            self.irc.redmine_domain,
            issue["id"]))
