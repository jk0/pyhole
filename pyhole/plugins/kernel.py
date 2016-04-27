#   Copyright 2011-2016 Josh Kearney
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

"""Pyhole Kernel.org Plugin"""

import re

from pyhole.core import plugin
from pyhole.core import utils


class Kernel(plugin.Plugin):
    """Provide access to kernel.org data."""

    @plugin.hook_add_command("kernel")
    @utils.spawn
    def kernel(self, message, params=None, **kwargs):
        """Retrieve the current kernel version (ex: .kernel)"""
        url = "https://www.kernel.org/kdist/finger_banner"
        response = utils.fetch_url(url)
        if response.status_code != 200:
            return

        r = re.compile("(.* mainline .*)")
        m = r.search(response.content)
        kernel = m.group(1).replace("  ", "")
        message.dispatch(kernel)
