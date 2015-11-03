#   Copyright 2011-2015 Josh Kearney
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

from BeautifulSoup import BeautifulSoup

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

    @plugin.hook_add_keyword("k")
    @utils.require_params
    @utils.spawn
    def keyword_k(self, message, params=None, **kwargs):
        """Retrieve kernel.org Bugzilla bug information (ex: K12345)"""
        params = utils.ensure_int(params)
        if not params:
            return

        params = {"id": params}
        url = "https://bugzilla.kernel.org/show_bug.cgi"
        response = utils.fetch_url(url, params=params)
        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.content)
        desc = utils.decode_entities(soup.head.title.string)

        try:
            status = soup.find("span", {"id": "static_bug_status"}).string
            status = status.capitalize().split("\n")[0]

            assignee = utils.decode_entities(
                soup.findAll("span", {
                    "class": "vcard"
                })[0].contents[0].string)

            msg = "%s [Status: %s, Assignee: %s] %s"
            message.dispatch(msg % (desc, status, assignee, url))
        except TypeError:
            return

    @plugin.hook_add_msg_regex(
        "https?:\/\/bugzilla\.kernel\.org\/show\_bug\.cgi\?id\=")
    def _watch_for_k_bug_url(self, message, params=None, **kwargs):
        """Watch for kernel.org Bugzilla bug URLs"""
        try:
            bug_id = message.message.split("id=", 1)[1].split(" ", 1)[0]
            self.keyword_k(message, bug_id)
        except TypeError:
            return
