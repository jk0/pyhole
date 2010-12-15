#   Copyright 2010 Josh Kearney
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

"""Pyhole Administration"""


import sys

from pyhole import utils


class Admin(object):
    """Provide administration functionality"""

    def __init__(self, irc):
        self.irc = irc

    def help(self, params=None):
        """Learn how to use active plugins (ex: .help <plugin.command>)"""
        if params:
            # Temporarily load the class for __doc__ access
            try:
                plugin = params.split(".")[0]
                exec("import %s\n%s = %s.%s(self.irc)" % (
                    plugin,
                    plugin.capitalize(),
                    plugin,
                    plugin.capitalize()))

                doc = eval("%s.__doc__" % params.capitalize())
                self.irc.say(doc)

                # Destroy the class
                exec("%s = None" % plugin.capitalize())
            except ImportError:
                self.irc.say("No plugin named '%s'" % params)
        else:
            self.irc.say(self.help.__doc__)
            self.irc.say(self.irc.active_commands())

    @utils.admin
    def reload(self, params=None):
        """Reload all plugins"""
        self.irc.load_plugins(reload_plugins=True)
        self.irc.say(self.irc.active_plugins())

    @utils.admin
    def info(self, params=None):
        """Access various statistics (ex: .info <topic>)"""
        if params == "channels":
            self.irc.say(self.irc.active_channels())
        else:
            self.irc.say(self.info.__doc__)

    @utils.admin
    def op(self, params=None):
        """Op a user (ex: .op <channel> <nick>)"""
        if params:
            self.irc.op_user(params)
        else:
            self.irc.say(self.op.__doc__)

    @utils.admin
    def nick(self, params=None):
        """Change IRC nick (ex: .nick <nick>)"""
        if params:
            self.irc.set_nick(params)
        else:
            self.irc.say(self.nick.__doc__)

    @utils.admin
    def join(self, params=None):
        """Join a channel (ex: .join #channel [<key>])"""
        if params:
            self.irc.join_channel(params)
        else:
            self.irc.say(self.join.__doc__)

    @utils.admin
    def part(self, params=None):
        """Part a channel (ex: .part <channel>)"""
        if params:
            self.irc.part_channel(params)
        else:
            self.irc.say(self.part.__doc__)

    @utils.admin
    def quit(self, params=None):
        """Quit and shutdown"""
        self.irc.say("Later!")
        self.irc.log.info("Shutting down")
        sys.exit(1)
