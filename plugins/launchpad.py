#   Copyright 2011 Paul Voccio
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

"""Pyhole Launchpad Plugin"""

from launchpadlib.launchpad import Launchpad as LP

from pyhole import utils


class Launchpad(object):
    """Provide access to Canonical's Launchpad"""

    def __init__(self, irc):
        self.irc = irc
        self.launchpad = LP.login_anonymously(
            "pyhole",
            "production",
            self.irc.cache)

    @utils.spawn
    def bugs(self, params=None):
        """Current bugs for a team (ex: .bugs <project> <team>|<user>)"""
        if params:
            project, team = params.split(" ")
            try:
                members = self.launchpad.people[team]
                proj = self.launchpad.projects[project]

                # Find a single member
                self._find_bugs(members, proj, True)

                # Find everyone on the team
                for person in members.members:
                    self.irc.log.debug("LP: %s" % person.display_name)
                    self._find_bugs(person, proj)
            except KeyError:
                self.irc.say("Unable to find user '%s' in Launchpad" % team)
        else:
            self.irc.say(self.bugs.__doc__)

    def _find_bugs(self, person, project, single=False):
        """Lookup Launchpad bugs"""
        bugs = project.searchTasks(assignee=person)
        if len(bugs):
            for bug in bugs:
                self.irc.say("%s by %s" % (bug.title, person.display_name))
                self.irc.say(bug.web_link)
        else:
            if single:
                self.irc.say("No bugs found for %s" % (person.display_name))
