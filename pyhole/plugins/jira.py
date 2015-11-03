#   Copyright 2015 Jason Meridth
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

"""Pyhole Jira Plugin"""

from jira import JIRA

from pyhole.core import plugin
from pyhole.core import utils


class Jira(plugin.Plugin):
    """Provide access to the Jira API"""

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__

        self.jira = utils.get_config("Jira")
        self.jira_domain = self.jira.get("domain")
        self.jira_username = self.jira.get("username")
        self.jira_password = self.jira.get("password")

        self.jira = JIRA(self.jira_url,
                         basic_auth=(self.jira_username,
                                     self.jira_password))

    @plugin.hook_add_keyword("jira")
    @utils.require_params
    @utils.spawn
    def keyword_jira(self, message, params=None, **kwargs):
        """Retrieve Jira ticket information (ex: jira NCP-1444)"""
        params = utils.ensure_int(params)
        if not params:
            return

        self._find_issue(message, params)

    def _find_issue(self, message, issue_id):
        """Find and display a Jira issue"""

        try:
            issue = self.jira.issue(issue_id)
        except Exception:
            return

        msg = "JIRA %s #%s: %s [S: %s, P: %s, L: %s, A: %s]" % (
            issue.fields.tracker.name, issue.id, issue.fields.summary,
            issue.fields.status.name, issue.fields.priority.name,
            ",".join(issue.fields.labels),
            issue.get("fields", {}).get("assignee", "N/A"))
        url = "https://%s/browse/%s" % (self.jira_url, issue.key)

        message.dispatch("%s %s" % (msg, url))
