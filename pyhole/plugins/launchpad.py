# Copyright 2011-2026 Paul Voccio and contributors
# SPDX-License-Identifier: Apache-2.0

"""Launchpad plugin (optional extra: pip install irc-pyhole[launchpad])."""

from __future__ import annotations

from pyhole.core import plugin, utils

try:
    from launchpadlib.launchpad import Launchpad as LP
except ImportError:  # pragma: no cover - optional extra
    LP = None


class Launchpad(plugin.Plugin):
    """Launchpad bug lookup."""

    def __init__(self, session):
        super().__init__(session)
        if LP is None:
            raise RuntimeError("launchpadlib is not installed; pip install 'irc-pyhole[launchpad]'")
        self.launchpad = LP.login_anonymously(
            "pyhole", "production", str(utils.get_directory(self.name))
        )

    @plugin.hook_add_command("lbugs")
    @utils.require_params
    @utils.spawn
    def lbugs(self, message, params=None, **kwargs):
        """Launchpad bugs for a team (ex: .lbugs <project> <team>|<user>)."""
        try:
            project, team = params.split(" ", 1)
        except ValueError:
            message.dispatch(self.lbugs.__doc__)
            return
        try:
            members = self.launchpad.people[team]
            proj = self.launchpad.projects[project]
        except KeyError:
            message.dispatch(f"Unable to find user '{team}' in Launchpad.")
            return

        people = list(members.members)
        if len(people) < 2:
            self._find_bugs(message, members, proj)
            return
        for i, person in enumerate(people):
            if i <= 4:
                self._find_bugs(message, person, proj, single=False)
            else:
                message.dispatch(f"[...] truncated last {len(people) - i} users")
                break

    @plugin.hook_add_keyword("lp")
    @utils.require_params
    @utils.spawn
    def keyword_lp(self, message, params=None, **kwargs):
        """Retrieve Launchpad bug information (ex: LP12345)."""
        bug_id = utils.ensure_int(params)
        if not bug_id:
            return
        try:
            bug = self.launchpad.bugs[bug_id]
            task = bug.bug_tasks[len(bug.bug_tasks) - 1]
            message.dispatch(
                f"LP {task.title} [Status: {task.status}, "
                f"Assignee: {self._find_name(task.assignee_link)}] {bug.web_link}"
            )
        except Exception:
            return

    @plugin.hook_add_msg_regex(r"https?://bugs\.launchpad\.net/.*/\+bug")
    def regex_match_lp_bug_url(self, message, params=None, **kwargs):
        """Watch for Launchpad bug URLs."""
        self._extract_bug(message, "+bug")

    @plugin.hook_add_msg_regex(r"https?://bugs\.launchpad\.net/bugs")
    def regex_match_short_lp_bug_url(self, message, params=None, **kwargs):
        """Watch for short Launchpad bug URLs."""
        self._extract_bug(message, "bugs")

    def _extract_bug(self, message, marker: str) -> None:
        try:
            parts = message.message.split("/")
            for i, word in enumerate(parts):
                if word == marker and i + 1 < len(parts):
                    self.keyword_lp(message, parts[i + 1].split(" ", 1)[0])
        except (TypeError, IndexError):
            return

    def _find_name(self, user):
        try:
            return self.launchpad.people[user].display_name
        except (ValueError, KeyError):
            return "None"

    def _find_bugs(self, message, person, project, single=True) -> None:
        bugs = list(project.searchTasks(assignee=person))
        if not bugs:
            if single:
                message.dispatch(f"No bugs found: {person.display_name}")
            return
        for i, bug in enumerate(bugs):
            if i <= 4:
                message.dispatch(f"LP {bug.title} [Assignee: {person.display_name}] {bug.web_link}")
            else:
                message.dispatch(f"[...] truncated last {len(bugs) - i} bugs")
                break
