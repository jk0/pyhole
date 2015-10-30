#   Copyright 2015 Rick Harris
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

"""Pyhole Scorekeeper Plugin

Scorekeeper is a fun way to playfully high-five or boo someone.

Each user gets a score which can be incremented like:
    <nick>++

The score can also be decremented like:
    <nick>--

The running highscore can displayed with:
    .score

An individual's score can be displayed with:
    .score <nick>
"""

from pyhole.core import plugin
from pyhole.core import utils


class Scorekeeper(plugin.Plugin):
    """Each user gets a score. Do with it what you want."""
    @plugin.hook_add_msg_regex("^(.+)\+\+")
    @utils.spawn
    def increment_score(self, message, match, **kwargs):
        nick = match.group(1)
        self._adjust_score(message, nick, 1)

    @plugin.hook_add_msg_regex("^(.+)\-\-")
    @utils.spawn
    def decrement_score(self, message, match, **kwargs):
        nick = match.group(1)
        self._adjust_score(message, nick, -1)

    def _adjust_score(self, message, nick, delta):
        score = self._get_score(nick)
        if score is None:
            score = 0
        score += delta
        utils.write_file(self.name, nick, str(score))
        message.dispatch(score)

    def _get_score(self, nick):
        score = utils.read_file(self.name, nick)
        if score is None:
            return None
        try:
            return int(score)
        except ValueError:
            return None

    def _display_highscores(self, message):
        scores = []
        for nick in utils.list_files(self.name):
            score = self._get_score(nick)
            scores.append((score, nick))

        if not scores:
            message.dispatch("No scores yet.")
            return

        message.dispatch("Highscores (Top 5)")
        message.dispatch("==================")
        scores.sort(reverse=True)
        for score, nick in scores[:5]:
            message.dispatch("%s %s" % (str(score).rjust(4),
                                        nick.rjust(13)))

    @plugin.hook_add_command("score")
    @utils.spawn
    def score(self, message, params=None, **kwargs):
        """Display highscores"""
        if params:
            nick = params.strip()
            score = self._get_score(nick)
            if score is None:
                return message.dispatch("No score found for '%s'." % nick)
            else:
                message.dispatch(score)
                return
        else:
            return self._display_highscores(message)
