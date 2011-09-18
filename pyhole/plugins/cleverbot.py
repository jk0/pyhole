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

"""Pyhole Cleverbot Plugin

needs the pycleverbot library from

browse latest: 
http://code.google.com/p/pycleverbot/downloads/list

get specific version:
wget http://code.google.com/p/pycleverbot/downloads/detail?name=cleverbot.py&can=2&q=
"""

import cleverbot

from pyhole import plugin
from pyhole import utils

class CleverChat(plugin.Plugin):
    """Provide access to the Cleverbot API"""

    @plugin.hook_add_command("chat")
    @utils.spawn
    def chat(self, params=None, **kwargs):
        """Chat with the Cleverbot (ex: .chat 'How you doin'?"""
        cb = cleverbot.Session()
        if params:
            try:
                self.irc.reply(cb.Ask(params))
            except KeyError:
                self.irc.reply("Can't chat now, I'm washing my hair")
        else:
            self.irc.reply(self.chat.__doc__)

