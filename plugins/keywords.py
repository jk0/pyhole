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

"""Pyhole Keyword Plugin"""


from launchpadlib.launchpad import Launchpad
from pyactiveresource.activeresource import ActiveResource

from pyhole import utils


class Keywords(object):
    """Watch for keywords in IRC messages"""

    def __init__(self, irc):
        self.irc = irc
        cachedir = ".cachedir"
        self.launchpad = Launchpad.login_anonymously('pyhole', 'production', cachedir) 
        #self.launchpad = Launchpad.login_anonymously("pyhole")

    @utils.spawn
    def keyword_lp(self, params=None):
        """Retrieve Launchpad bug information (ex: LP12345)"""
        if params:
            try:
                int(params)
            except ValueError:
                return

            try:
                bug = self.launchpad.bugs[params]

                self.irc.say("Launchpad bug #%s: %s [%s]" % (
                    bug.id,
                    bug.title,
                    bug.bug_tasks[len(bug.bug_tasks) - 1].status))
            except Exception:
                return

    @utils.spawn
    def keyword_rm(self, params=None):
        """Retrieve Redmine bug information (ex: RM12345)"""
        if params:
            try:
                int(params)
            except ValueError:
                return

            class Issue(ActiveResource):
                _site = "https://redmine.domain"
                _user = "username"
                _password = "password"

            try:
                issue = Issue.find(params)

                self.irc.say("Redmine bug #%s: %s" % (
                    issue.id,
                    issue.subject))
            except Exception:
                return
