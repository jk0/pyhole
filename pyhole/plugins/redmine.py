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

"""Pyhole Redmine Plugin"""

from pyhole.core import plugin
from pyhole.core import utils


class Redmine(plugin.Plugin):
    """Provide access to the Redmine API."""

    def __init__(self, session):
        self.session = session
        self.name = self.__class__.__name__

        self.redmine = utils.get_config("Redmine")
        self.redmine_domain = self.redmine.get("domain")
        self.redmine_key = self.redmine.get("key")
        self.redmine_url = "https://%s:password@%s" % (
            self.redmine_key, self.redmine_domain)

    @plugin.hook_add_command("rbugs")
    @utils.require_params
    @utils.spawn
    def rbugs(self, message, params=None, **kwargs):
        """Redmine bugs for a user (ex: .rbugs <login>)."""
        login = params.split(" ", 1)[0]
        user_id = self._find_user(login)

        i = 0
        issues = self._find_issues(user_id)
        for i, issue in enumerate(issues):
            if i <= 4:
                self._find_issue(message, issue["id"])
            else:
                message.dispatch("[...] truncated last %d bugs" % (
                                 len(issues) - i))
                break
        else:
            if i <= 0:
                message.dispatch("No Redmine bugs found: '%s'" % login)

    @plugin.hook_add_keyword("rm")
    @utils.require_params
    @utils.spawn
    def keyword_rm(self, message, params=None, **kwargs):
        """Retrieve Redmine bug information (ex: RM12345)."""
        params = utils.ensure_int(params)
        if params:
            self._find_issue(message, params)

    @plugin.hook_add_msg_regex("https?:\/\/redmine\..*/issues")
    def regex_match_rm_bug_url(self, message, params=None, **kwargs):
        """Watch for Redmine bug URLs."""
        try:
            line = message.message.split("/")
            for i, word in enumerate(line):
                if word == "issues":
                    bug_id = line[i + 1].split(" ", 1)[0]
                    self.keyword_rm(bug_id)
        except TypeError:
            return

    def _find_issues(self, user_id):
        """Find all issues for a Redmine user."""
        url = "%s/issues.json?assigned_to_id=%s" % (
              self.redmine_url, user_id)
        response = utils.fetch_url(url)
        if response.status_code != 200:
                return

        return response.json()["issues"]

    def _find_user(self, login):
        """Find a specific Redmine user."""
        for user in self._find_users():
            if login == user["login"]:
                return user["id"]

        for user in self._find_users(100):
            if login == user["login"]:
                return user["id"]

    def _find_users(self, offset=None):
        """Find all Redmine users."""
        if offset:
            url = "%s/users.json?limit=100&offset=%d" % (
                  self.redmine_url, offset)
        else:
            url = "%s/users.json?limit=100" % self.redmine_url
        response = utils.fetch_url(url)
        if response.status_code != 200:
                return

        return response.json()["users"]

    def _find_issue(self, message, issue_id):
        """Find and display a Redmine issue."""
        url = "%s/issues/%s.json" % (self.redmine_url, issue_id)
        response = utils.fetch_url(url)
        if response.status_code != 200:
                return

        try:
            issue = response.json()["issue"]
        except Exception:
            return

        msg = "RM %s #%s: %s [Status: %s, Priority: %s, Assignee: %s]" % (
            issue["tracker"]["name"],
            issue["id"],
            issue["subject"],
            issue["status"]["name"],
            issue["priority"]["name"],
            issue.get("assigned_to", {}).get("name", "N/A"))
        url = "https://%s/issues/%s" % (self.redmine_domain, issue["id"])

        message.dispatch("%s %s" % (msg, url))
