#   Copyright 2010-2011 Josh Kearney
#   Copyright 2012 Aaron Lee
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

"""Pyhole Topher Plugin"""

import random

from pyhole import plugin
from pyhole import utils

phrases = [
    "Low bros before big bros",
    "Hey guys, I'm actually gonna go do a bunch of errands right now",
    "They live in the Penthouse penthouse. Thats like the Playboy"
    " Mansion only this time its much more doper",
    "Chill out. I told them that you three are coke dealers, and they"
    " all have really bad coke problems" ]


class Topher(plugin.Plugin):
    """I'm a beliber"""

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
        self.config = utils.get_config("Topher")

    def say_hi(self, source, target):
        greeting = self.config.get("greeting")
        if not greeting:
            return

        if source == self.irc.nick:
            self.irc.connection.privmsg(target, greeting)

    @plugin.hook_add_action("join")
    def join(self, params=None, **kwargs):
        target = kwargs.get("target")
        source = params
        if not source or not target:
            return
        self.say_hi(source, target)

    @plugin.hook_add_command("hi")
    def hi(self, params=None, **kwargs):
        greeting = self.config.get("greeting")
        if not greeting:
            return

        self.irc.reply(greeting)

    @plugin.hook_add_msg_regex('smoke')
    def smoke(self, params=None, **kwargs):
        self.irc.reply('But never with the trooooooooooon...')

    @plugin.hook_add_msg_regex('.')
    def catchphrase(self, params=None, **kwargs):
        chance = random.randint(0, 100)
        if chance == 1:
            phrases_count = len(phrases)
            which_phrase = random.randint(0, phrases_count-1)
            self.irc.reply(phrases[which_phrase])

    @plugin.hook_add_msg_regex('\?')
    def piss_roof(self, params=None, **kwargs):
        chance = random.randint(0, 10)
        if chance == 1:
            self.irc.reply("Yeah, if you don't mind if I take a piss "
                           "off your roof first")
