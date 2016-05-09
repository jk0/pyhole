#   Copyright 2016 Josh Kearney
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

import json

from pyhole.core import plugin
from pyhole.core import utils


class JiraClient(object):
    def __init__(self):
        jira = utils.get_config("Jira")

        self.auth_server = jira.get("auth_server")
        self.domain = jira.get("domain")
        self.username = jira.get("username")
        self.password = jira.get("password")

    def get(self, issue_id):
        url = "%s/rest/api/latest/issue/%s" % (self.auth_server, issue_id)

        return utils.fetch_url(url, verify=False,
                               auth=(self.username, self.password))


class Jira(plugin.Plugin):
    """Provide access to the Jira API."""

    def __init__(self, session):
        self.session = session
        self.name = self.__class__.__name__

        self.client = JiraClient()

    @plugin.hook_add_msg_regex("([A-Z]{2}-[0-9]{3,5})")
    def regex_match_issue(self, message, match, **kwargs):
        """Retrieve Jira ticket information (ex: AB-1234)."""
        try:
            issue_id = match.group(0)
            self._find_issue(message, issue_id)
        except Exception:
            return

    @utils.spawn
    def _find_issue(self, message, issue_id):
        """Find and display a Jira issue."""
        issue = json.loads(self.client.get(issue_id).content)["fields"]

        assignee = issue.get("assignee")
        if assignee:
            assignee = assignee.get("displayName")

        msg = "%s: %s [Status: %s, Priority: %s, Assignee: %s] %s"
        message.dispatch(msg % (
            issue_id,
            issue["summary"],
            issue["status"]["name"],
            issue["priority"]["name"],
            assignee,
            "%s/jira/browse/%s" % (self.client.domain, issue_id)
        ))
