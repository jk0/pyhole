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
    def teambugs(self, params=None):
        """Display current bugs for a team (ex: .bugs <project> <team>|<user>)"""
        if params:
            project, team = params.split(" ")
            members = self.launchpad.people[team]
            proj = self.launchpad.projects[project]
            #find a single member
            self._find_bugs(members, proj)
            #find everyone on the team
            for person in members.members:
                self.irc.log.debug("LP: Looking up %s" % person.display_name)
                self._find_bugs(person, proj)
        else:
            self.irc.say(self.bugs.__doc__)

    def _find_bugs(self, person, proj):
        """Lookup Launchpad bugs"""
        bugs = proj.searchTasks(assignee=person)
        for b in bugs:
            self.irc.say("%s %s" % (person.display_name, b.web_link))
            self.irc.say(b.title)
