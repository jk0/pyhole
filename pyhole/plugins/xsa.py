#   Copyright 2015-2016 Rick Harris
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

"""Pyhole Xen Security Advisory (XSA) Plugin"""

import json

from BeautifulSoup import BeautifulSoup

from pyhole.core import plugin
from pyhole.core import utils


class Xsa(plugin.Plugin):
    """Display information regarding Xen Security Advisories (XSAs)."""
    XSA_URL = "http://xenbits.xen.org/xsa/"

    @plugin.hook_add_keyword("xsa")
    @utils.require_params
    @utils.spawn
    def keyword_xsa(self, message, params=None, **kwargs):
        """Retrieve XSA information (ex: xsa123 or xsa-123)."""
        # abs is needed in case we get 'xsa-123', that would be -123
        xsa_num = abs(utils.ensure_int(params))
        xsa_id = "XSA-%d" % xsa_num
        data = self._load_cached_xsa_data()
        msg = self._make_xsa_message(xsa_id, data)
        if not msg:
            msg = "Unable to find matching XSA."
        message.dispatch(msg)

    def _make_xsa_message(self, xsa_id, data):
        try:
            xsa_info = data[xsa_id]
        except:
            return None
        else:
            # Use ID if we don't have a link
            if not xsa_info["link"]:
                xsa_info["link"] = xsa_info["id"]
            return ("%(link)s: %(title)s (Public Release: %(public_release)s)"
                    % xsa_info)

    @plugin.hook_add_poll("poll_xsa_list", poll_timer=300)
    def poll_xsa_list(self, message, params=None, **kwargs):
        old_data = self._load_cached_xsa_data()

        new_data = self._fetch_xsa_data()
        if not new_data:
            return

        new_data_json = json.dumps(new_data)
        utils.write_file(self.name, "xsas.json", new_data_json)

        # Notify subscribed channels on new XSAs
        old_xsa_ids = set(old_data.keys())
        new_xsa_ids = set(new_data.keys())
        added_xsa_ids = new_xsa_ids - old_xsa_ids
        if old_xsa_ids and added_xsa_ids:
            self._notify_new_xsas(added_xsa_ids, new_data)

    def _notify_new_xsas(self, added_xsa_ids, new_data):
        xsa_config = utils.get_config("XSA")
        try:
            notify_str = xsa_config.get("notify")
        except Exception:
            return

        channels = notify_str.split(",")
        for xsa_id in added_xsa_ids:
            msg = self._make_xsa_message(xsa_id, new_data)
            for channel in channels:
                channel = channel.strip()
                self.irc.notice(channel, msg)

    def _load_cached_xsa_data(self):
        data_json = utils.read_file(self.name, "xsas.json")
        if data_json is None:
            return {}
        return json.loads(data_json)

    def _fetch_xsa_data(self):
        resp = utils.fetch_url(self.XSA_URL)
        if resp.status_code != 200:
            print "Error fetching XSAs: %s" % resp.status_code
            return {}
        soup = BeautifulSoup(resp.text)
        rows = soup.findAll("tr")
        data = {}
        for row in rows:
            children = row.findChildren("td")
            if not children:
                continue
            try:
                xsa_id = children[0].contents[0].string
            except:
                continue
            try:
                xsa_link = "".join([self.XSA_URL,
                                    children[0].contents[0]["href"]])
            except:
                xsa_link = None
            try:
                public_release = children[1].contents[0]
            except:
                public_release = None
            try:
                title = children[5].contents[0]
            except:
                title = None
            data[xsa_id] = {"id": xsa_id,
                            "link": xsa_link,
                            "public_release": public_release,
                            "title": title}
        return data
