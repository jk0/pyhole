#   Copyright 2016 Josh Kearney
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

"""Pyhole On-Call Plugin"""

from pyhole.core import plugin
from pyhole.core import utils
import requests


class OnCall(plugin.Plugin):
    """Manage on-call duties."""

    def __init__(self, session):
        self.session = session
        self.name = self.__class__.__name__
        self.level = "GREEN"
        pagerduty = utils.get_config("PagerDuty")
        self.subdomain = pagerduty.get("subdomain")
        self.apikey = pagerduty.get("apikey")

    @plugin.hook_add_command("note")
    @utils.require_params
    @utils.spawn
    def note(self, message, params=None, **kwargs):
        """Manage notes during an outage (ex: .note <message>)."""
        return

    @plugin.hook_add_command("status")
    @utils.require_params
    @utils.spawn
    def status(self, message, params=None, **kwargs):
        """Manage status of a service (ex: .status <service> [<status>])."""
        return

    @plugin.hook_add_command("threat")
    def threat(self, message, params=None, **kwargs):
        """Set the current threat level (ex: .threat [<level>])."""
        levels = ("RED", "ORANGE", "YELLOW", "BLUE", "GREEN")

        if params:
            self.level = params.split(" ", 1)[0].upper()
            if self.level in levels:
                message.dispatch("Threat Level: %s" % self.level)
            else:
                message.dispatch("Available Levels: %s" % ", ".join(levels))
        else:
            message.dispatch("Threat Level: %s" % self.level)
            return

    @plugin.hook_add_command("oncall")
    def whois(self, message, params=None, **kwargs):
        """Show who is oncall for one/all schedules"""
        url = 'https://{0}.pagerduty.com/api/v1/escalation_policies/on_call'.\
            format(self.subdomain)
        headers = {
            'Authorization': 'Token token={0}'.format(self.apikey),
            'Content-Type': 'application/json',
        }

        if params:
            filters = {
                'query': params,
            }
        else:
            filters = self.default_filter


        r = requests.get(url, headers=headers, params=filters)
        for ep in r.json()['escalation_policies']:
            print ep['name']
            msg = '%s:\n' % ep['name']
            for level in ep['on_call']:
                msg += 'Level %s: %s %s\n' % (level['level'],
                                            level['user']['name'],
                                            level['user']['email'])
            message.dispatch(msg)
