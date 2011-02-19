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

"""Pyhole Launchpad Plugin"""


import pywapi

from pyhole import utils

from launchpadlib.launchpad import Launchpad as LP
import eventlet
import urllib
from eventlet.green import urllib2


class Launchpad(object):

    """Provide access to Canonical's Launchpad http://launchpad.net"""

    def __init__(self, irc):
        self.irc = irc

    @utils.spawn
    def bugs(self, params=None):
        """Display current bugs for team (ex: .bugs <project> <team>)"""

        doc = urllib.urlopen("https://blueprints.launchpad.net/nova")
        cachedir = ".cachedir"
        launchpad = LP.login_anonymously('pyhole', 'production', cachedir)
        pool = eventlet.GreenPool()
        project, team = params.split(" ")
        ozone = launchpad.people[team]
        proj = launchpad.projects[project]
        for person in ozone.members:
            print "Checking " + person.display_name
            self.find_bugs(person, proj)

    def find_bugs(self, person, proj):
        if str(person) == "None":
            next
        bugs = proj.searchTasks(assignee=person)
        for b in bugs:
            self.irc.say(person.display_name + " " + b.web_link)
            self.irc.say(b.titleg)
