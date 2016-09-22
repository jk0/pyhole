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

"""Pyhole Operations Plugin"""

from pyhole.core import plugin
from pyhole.core import request
from pyhole.core import utils


class Ops(plugin.Plugin):
    """Manage operational responsibilities."""

    def __init__(self, session):
        self.session = session
        self.name = self.__class__.__name__

        pagerduty = utils.get_config("PagerDuty")
        self.api_token = pagerduty.get("api_token")
        self.endpoint = "https://api.pagerduty.com"

        self.api_headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": "Token token=%s" % self.api_token,
            "Content-Type": "application/json"
        }

    @plugin.hook_add_command("oncall")
    @utils.spawn
    def oncall(self, message, params=None, **kwargs):
        """Show who is on call (ex: .oncall)."""
        url = "%s/oncalls" % self.endpoint
        req = request.get(url, headers=self.api_headers)
        if request.ok(req):
            response_json = req.json()
            on_calls = []
            for policy in response_json["oncalls"]:
                if policy["schedule"]:
                    on_calls.append("%s (%s)" % (policy["schedule"]["summary"],
                                                 policy["user"]["summary"]))
            message.dispatch(", ".join(on_calls))
        else:
            message.dispatch("Unable to fetch list: %d" % req.status_code)

    @plugin.hook_add_command("note")
    @utils.require_params
    @utils.spawn
    def note(self, message, params=None, **kwargs):
        """Create a note for an incident (ex: .note <ID> <message>)."""
        params = params.split(" ")
        incident_id = params.pop(0)

        users = self._find_users(message.source)
        if len(users["users"]) < 1:
            message.dispatch("Unable to find user: %s" % message.source)
            return

        self.api_headers["From"] = users["users"][0]["email"]
        data = {
            "note": {
                "content": " ".join(params)
            }
        }

        url = "%s/incidents/%s/notes" % (self.endpoint, incident_id)
        req = request.post(url, headers=self.api_headers, json=data)

        if request.ok(req):
            message.dispatch("Noted.")
        else:
            message.dispatch("Unable to create note: %d" % req.status_code)
            message.dispatch(req.text)

    @plugin.hook_add_command("notes")
    @utils.require_params
    @utils.spawn
    def notes(self, message, params=None, **kwargs):
        """List all notes an incident (ex: .note <ID>)."""
        url = "%s/incidents/%s/notes" % (self.endpoint, params)
        req = request.get(url, headers=self.api_headers)

        if request.ok(req):
            response_json = req.json()
            notes = response_json["notes"]
            message.dispatch("There are %d notes." % len(notes))

            for note in notes:
                message.dispatch("%s %s - %s" % (note["created_at"],
                                                 note["user"]["summary"],
                                                 note["content"]))
        else:
            message.dispatch("Unable to fetch notes: %d" % req.status_code)

    @plugin.hook_add_command("lookup")
    @utils.require_params
    @utils.spawn
    def lookup(self, message, params=None, **kwargs):
        """Lookup user's phone numbers (ex: .lookup <name>."""
        users = self._find_users(params)

        results = []
        for user in users["users"]:
            for contact in user["contact_methods"]:
                if contact["type"] == "phone_contact_method":
                    results.append("%s (%s)" % (user["name"],
                                                contact["address"]))
        if len(results) > 0:
            message.dispatch(", ".join(results))
        else:
            message.dispatch("No results found: %s" % params)

    def _find_users(self, name):
        """Find PagerDuty user account information."""
        url = "%s/users?query=%s&include[]=contact_methods" % (self.endpoint,
                                                               name)
        req = request.get(url, headers=self.api_headers)
        if request.ok(req):
            return req.json()
