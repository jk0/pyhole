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

"""Pyhole task plugin"""

import os
import readline
import re
import subprocess as sub
from pyhole import plugin


class Task(plugin.Plugin):
    """Provide access to task manager"""

    @plugin.hook_add_command("task")
    def task (self, params=None, **kwargs):
        """List tasks (ex: .task list) http://taskwarrior.org/projects/show/taskwarrior/"""
        if params:
            verb = params.split()[0]
            source = self.irc.source.split("!")[0]
            params = "%s project:%s" % (params,source)
            # r = re.compile("(.* mainline .*)")
            # m = r.search(response.read())
            for w in ['list', 'add', '^\d+']:
                r = re.compile(w)
                m = r.search(verb)
                if m:
                    self._run(params)
        else:
            result = self.task.__doc__

    def _run (self, params):
        source = self.irc.source.split("!")[0]
        params = "%s project:%s" % (params,source)
        
        try:
            cmd = "/usr/bin/task"
            p = sub.Popen([cmd] + params.split(), stdout=sub.PIPE,stderr=sub.PIPE)
            result, error = p.communicate()
        except EOFError:
            self.irc.reply("can't find task binary")
        self.irc.reply("%s: %s" % (source, result))
