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

"""Pyhole Taskwarrior Plugin"""

import subprocess

from pyhole import plugin


class Taskwarrior(plugin.Plugin):
    """Provide access to Taskwarrior"""

    @plugin.hook_add_command("task")
    def task(self, params=None, **kwargs):
        """List and add tasks (ex: .task <list|add|done>)"""
        if params:
            verb = params.split(" ", 1)[0]
            source = self.irc.source.split("!")[0]
            params = "%s project:%s" % (params, source)

            for command in ["list", "add", "done"]:
                if verb == command:
                    self._run(params)
        else:
            self.irc.reply(self.task.__doc__)

    def _run(self, params):
        """Execute the Taskwarrior binary"""
        try:
            p = subprocess.Popen(["task"] + params.split(" "),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result, error = p.communicate()

            self.irc.reply(result)
        except Exception:
            self.irc.reply("Unable to load Taskwarrior")
