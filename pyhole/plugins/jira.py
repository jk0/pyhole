# Copyright 2016-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Jira plugin."""

from __future__ import annotations

from pyhole.core import plugin, request, utils


class JiraClient:
    def __init__(self) -> None:
        jira = utils.get_config("Jira")
        self.auth_server = jira.get("auth_server")
        self.domain = jira.get("domain")
        self.username = jira.get("username")
        self.password = jira.get("password")
        self.verify_ssl = jira.get("verify_ssl", type="bool", default=True)

    def get(self, issue_id: str):
        url = f"{self.auth_server}/rest/api/latest/issue/{issue_id}"
        return request.get(
            url,
            verify=self.verify_ssl,
            auth=(self.username, self.password),
        )


class Jira(plugin.Plugin):
    """Jira ticket lookup."""

    def __init__(self, session):
        super().__init__(session)
        self.client = JiraClient()

    @plugin.hook_add_msg_regex(r"([A-Z]{2}-[0-9]{3,5})")
    def regex_match_issue(self, message, match, **kwargs):
        """Retrieve Jira ticket information (ex: AB-1234)."""
        try:
            self._find_issue(message, match.group(0))
        except Exception:
            return

    @utils.spawn
    def _find_issue(self, message, issue_id: str) -> None:
        try:
            issue = self.client.get(issue_id).json()["fields"]
        except (KeyError, ValueError, TypeError):
            return
        assignee = (issue.get("assignee") or {}).get("displayName")
        message.dispatch(
            f"{issue_id}: {issue['summary']} [Status: {issue['status']['name']}, "
            f"Priority: {issue['priority']['name']}, Assignee: {assignee}] "
            f"{self.client.domain}/jira/browse/{issue_id}"
        )
