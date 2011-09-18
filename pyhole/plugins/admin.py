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

from pyhole import irc
from pyhole import plugin
from pyhole import utils


class Admin(plugin.Plugin):
    """Provide administration functionality"""

    @plugin.hook_add_command("help")
    def help(self, params=None, **kwargs):
        """Learn how to use active commands (ex: .help <command>)"""

        if params:
            doc = self._find_doc_string(params)
            if doc:
                self.irc.reply(doc)
            else:
                self.irc.reply("No help available for %s" % params)
        else:
            self.irc.reply(self.help.__doc__)
            self.irc.reply("Active Commands: %s" % irc.active_commands())
            self.irc.reply("Active Keywords: %s" % irc.active_keywords())

    @plugin.hook_add_command("version")
    def version(self, params=None, **kwargs):
        """Display the current version"""
        self.irc.reply(self.irc.version)

    @plugin.hook_add_command("reload")
    @utils.admin
    def reload(self, params=None, **kwargs):
        """Reload all plugins"""
        self.irc.load_plugins(reload_plugins=True)
        self.irc.reply("Loaded Plugins: %s" % irc.active_plugins())

    @plugin.hook_add_command("op")
    @utils.admin
    def op(self, params=None, **kwargs):
        """Op a user (ex: .op <channel> <nick>)"""
        if params:
            self.irc.op_user(params)
        else:
            self.irc.reply(self.op.__doc__)

    @plugin.hook_add_command("deop")
    @utils.admin
    def deop(self, params=None, **kwargs):
        """De-op a user (ex: .deop <channel> <nick>)"""
        if params:
            self.irc.deop_user(params)
        else:
            self.irc.reply(self.deop.__doc__)

    @plugin.hook_add_command("nick")
    @utils.admin
    def nick(self, params=None, **kwargs):
        """Change IRC nick (ex: .nick <nick>)"""
        if params:
            self.irc.set_nick(params)
        else:
            self.irc.reply(self.nick.__doc__)

    @plugin.hook_add_command("join")
    @utils.admin
    def join(self, params=None, **kwargs):
        """Join a channel (ex: .join #channel [<key>])"""
        if params:
            self.irc.join_channel(params)
        else:
            self.irc.reply(self.join.__doc__)

    @plugin.hook_add_command("part")
    @utils.admin
    def part(self, params=None, **kwargs):
        """Part a channel (ex: .part <channel>)"""
        if params:
            self.irc.part_channel(params)
        else:
            self.irc.reply(self.part.__doc__)

    @plugin.hook_add_command("say")
    @utils.admin
    def say(self, params=None, **kwargs):
        """Send a PRIVMSG (ex: .say <channel>|<nick> message)"""
        if params:
            (target, msg) = params.split(" ", 1)
            self.irc.privmsg(target, msg)
        else:
            self.irc.reply(self.say.__doc__)

    def _find_doc_string(self, params):
        """Find the doc string for a plugin, command or keyword hook"""
        for p in plugin.active_plugin_classes():
            if p.__name__.upper() == params.upper():
                return p.__doc__

        for _, cmd_hook, cmd in plugin.hook_get_commands():
            if cmd.upper() == params.upper():
                return cmd_hook.__doc__

        for _, kw_hook, kw in plugin.hook_get_keywords():
            if kw.upper() == params.upper():
                return kw_hook.__doc__

        return None
