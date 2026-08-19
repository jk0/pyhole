# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Redmine plugin."""

from __future__ import annotations

from pyhole.core import plugin, request, utils


class Redmine(plugin.Plugin):
    """Redmine bug lookup."""

    def __init__(self, session):
        super().__init__(session)
        redmine = utils.get_config("Redmine")
        self.domain = redmine.get("domain")
        self.key = redmine.get("key")
        self.base_url = f"https://{self.domain}"
        self.headers = {"X-Redmine-API-Key": self.key}

    @plugin.hook_add_command("rbugs")
    @utils.require_params
    @utils.spawn
    def rbugs(self, message, params=None, **kwargs):
        """Redmine bugs for a user (ex: .rbugs <login>)."""
        login = params.split(" ", 1)[0]
        user_id = self._find_user(login)
        if not user_id:
            message.dispatch(f"No Redmine bugs found: '{login}'")
            return
        issues = self._find_issues(user_id) or []
        if not issues:
            message.dispatch(f"No Redmine bugs found: '{login}'")
            return
        for i, issue in enumerate(issues):
            if i <= 4:
                self._find_issue(message, issue["id"])
            else:
                message.dispatch(f"[...] truncated last {len(issues) - i} bugs")
                break

    @plugin.hook_add_keyword("rm")
    @utils.require_params
    @utils.spawn
    def keyword_rm(self, message, params=None, **kwargs):
        """Retrieve Redmine bug information (ex: RM12345)."""
        issue_id = utils.ensure_int(params)
        if issue_id:
            self._find_issue(message, issue_id)

    @plugin.hook_add_msg_regex(r"https?://redmine\..*/issues")
    def regex_match_rm_bug_url(self, message, params=None, **kwargs):
        """Watch for Redmine bug URLs."""
        try:
            parts = message.message.split("/")
            for i, word in enumerate(parts):
                if word == "issues" and i + 1 < len(parts):
                    bug_id = parts[i + 1].split(" ", 1)[0]
                    self.keyword_rm(message, bug_id)
        except (TypeError, IndexError):
            return

    def _find_issues(self, user_id):
        url = f"{self.base_url}/issues.json?assigned_to_id={user_id}"
        response = request.get(url, headers=self.headers)
        if response.status_code != 200:
            return []
        return response.json().get("issues", [])

    def _find_user(self, login):
        for offset in (None, 100):
            for user in self._find_users(offset):
                if login == user.get("login"):
                    return user.get("id")
        return None

    def _find_users(self, offset=None):
        if offset:
            url = f"{self.base_url}/users.json?limit=100&offset={offset}"
        else:
            url = f"{self.base_url}/users.json?limit=100"
        response = request.get(url, headers=self.headers)
        if response.status_code != 200:
            return []
        return response.json().get("users", [])

    def _find_issue(self, message, issue_id) -> None:
        url = f"{self.base_url}/issues/{issue_id}.json"
        response = request.get(url, headers=self.headers)
        if response.status_code != 200:
            return
        try:
            issue = response.json()["issue"]
        except Exception:
            return
        msg = (
            f"RM {issue['tracker']['name']} #{issue['id']}: {issue['subject']} "
            f"[Status: {issue['status']['name']}, Priority: {issue['priority']['name']}, "
            f"Assignee: {issue.get('assigned_to', {}).get('name', 'N/A')}]"
        )
        url = f"{self.base_url}/issues/{issue['id']}"
        message.dispatch(f"{msg} {url}")
