#   Copyright 2013 Rackspace Hosting 
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

"""Pyhole Plugin to map VersionOne username with nick"""

import json

from pyhole import plugin
from pyhole.plugins import mapping_utils
from pyhole import utils


class V1ircnick(plugin.Plugin):
    """Associates the irc nick with V1 username"""

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
	self.mapping_file = "v1ircnick"

    def help_display(self):
	"""Shows the help for all the commands that can be used"""
	self.irc.reply(".v1i set [<IRC nick>] [<V1 username>]")
	self.irc.reply(".v1i show [<IRC nick>]")
	self.irc.reply(".v1i list")

    def get_v1_username(self, sub_command):
        """Retrieves the V1 username assciated with the IRC nick"""
        key, value = mapping_utils.show(self.name, self.mapping_file, sub_command)
        return value

    @plugin.hook_add_command("v1ircnick")
    @utils.spawn
    def v1ircnick(self, params=None, **kwargs):
        """Set or display IRC nick to V1 username mappings syntax:
        .v1i <sub_command> [IRC nick] [V1 username]
        .v1i set honeybadger sweety
        .v1i show honeybadger
        .v1i unset honeybadger
        .v1i list
        """
        if params:
            sub_command = params
            if sub_command.startswith("set "):
		key, value = mapping_utils.assign(self.name, self.mapping_file, sub_command)
                self.irc.reply("IRC nick and V1 username association saved as %s <-> %s" % (key, value))

            if sub_command.startswith("unset "):
		key, value = mapping_utils.unassign(self.name, self.mapping_file, sub_command)
                self.irc.reply("unassigned IRC nick %s and V1 username %s association" % (key, value))

            if sub_command.startswith("show "):
                key, value = mapping_utils.show(self.name, self.mapping_file, sub_command)
                if not value:
                    self.irc.reply("There is no association with any V1 username for the given IRC nick %s" % key)
                else:
                    self.irc.reply("IRC nick %s <-> V1 username %s" % (key, value))

            if sub_command.startswith("list"):
		data = mapping_utils.list_display(self.name, self.mapping_file)
                if not data:
                    self.irc.reply("There are no associations of any nick with V1 username")
                else:
                    self.irc.reply("IRC nick <-> V1 username")
                    for nick, username in data:
                        self.irc.reply("%s <-> %s" % (nick, username))
			
            if sub_command.startswith("help"):
		self.help_display()
			
        else:
                self.irc.reply(self.v1ircnick.__doc__)
                return

    @plugin.hook_add_command("v1i")
    def alias_w(self, params=None, **kwargs):
        """Alias of v1ircnick"""
        self.v1ircnick(params, **kwargs)
