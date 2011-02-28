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

"""Pyhole Administration Plugin"""

from pyhole import utils
from pyhole import plugin


class Admin(plugin.Plugin):
    """Provide administration functionality"""

    @plugin.Plugin.command_hook('help')
    def help(self, params=None, **kwarg):
        """Learn how to use active plugins (ex: .help <plugin.command>)"""
        if params:
            # Temporarily load the class for __doc__ access
            try:
                doc = plugin.Plugin.get_command_doc(params)
                if doc:
                    self.irc.say(doc)
                else:
                    self.irc.say("No help available for %s" % params)
            except ImportError:
                self.irc.say("No plugin named '%s'" % params)
        else:
            self.irc.say(self.help.__doc__)
            self.irc.say("Active commands: %s" % self.irc.active_commands())
            self.irc.say("Active Keywords: %s" % self.irc.active_keywords())

    @plugin.Plugin.command_hook('version')
    def version(self, params=None, **kwarg):
        """Display the current version"""
        self.irc.say(self.irc.version)

    @plugin.Plugin.command_hook('reload')
    @utils.admin
    def reload(self, params=None, **kwarg):
        """Reload all plugins"""
        self.irc.load_plugins(reload_plugins=True)
        self.irc.say(self.irc.active_plugins())

    @plugin.Plugin.command_hook('op')
    @utils.admin
    def op(self, params=None, **kwarg):
        """Op a user (ex: .op <channel> <nick>)"""
        if params:
            self.irc.op_user(params)
        else:
            self.irc.say(self.op.__doc__)

    @plugin.Plugin.command_hook('deop')
    @utils.admin
    def deop(self, params=None, **kwarg):
        """De-op a user (ex: .deop <channel> <nick>)"""
        if params:
            self.irc.deop_user(params)
        else:
            self.irc.say(self.deop.__doc__)

    @plugin.Plugin.command_hook('nick')
    @utils.admin
    def nick(self, params=None, **kwarg):
        """Change IRC nick (ex: .nick <nick>)"""
        if params:
            self.irc.set_nick(params)
        else:
            self.irc.say(self.nick.__doc__)

    @plugin.Plugin.command_hook('join')
    @utils.admin
    def join(self, params=None, **kwarg):
        """Join a channel (ex: .join #channel [<key>])"""
        if params:
            self.irc.join_channel(params)
        else:
            self.irc.say(self.join.__doc__)

    @plugin.Plugin.command_hook('part')
    @utils.admin
    def part(self, params=None, **kwarg):
        """Part a channel (ex: .part <channel>)"""
        if params:
            self.irc.part_channel(params)
        else:
            self.irc.say(self.part.__doc__)
