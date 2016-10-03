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
from pyhole.core import version


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

    @plugin.hook_add_command("query")
    @utils.require_params
    @utils.spawn
    def query(self, message, params=None, **kwargs):
        """Query an incident (ex: .query <ID>)."""
        url = "%s/incidents/%s" % (self.endpoint, params)
        req = request.get(url, headers=self.api_headers)

        if request.ok(req):
            incident = req.json()["incident"]
            summary = incident["summary"]
            status = incident["status"]
            link = incident["html_url"]

            message.dispatch("%s [%s]: %s" % (summary, status, link))
        else:
            message.dispatch("Unable to query incident: %d" % req.status_code)
            message.dispatch(req.text)

    @plugin.hook_add_command("ack")
    @utils.require_params
    @utils.spawn
    def ack(self, message, params=None, **kwargs):
        """Acknowledge an incident (ex: .ack <ID>)."""
        self.api_headers["From"] = self._find_user(message.source)

        data = {
            "incidents": [{
                "id": params,
                "type": "incident",
                "status": "acknowledged"
            }]
        }

        url = "%s/incidents" % self.endpoint
        req = request.put(url, headers=self.api_headers, json=data)

        if request.ok(req):
            message.dispatch("Acknowledged.")
        else:
            message.dispatch("Unable to ack incident: %d" % req.status_code)
            message.dispatch(req.text)

    @plugin.hook_add_command("resolve")
    @utils.require_params
    @utils.spawn
    def resolve(self, message, params=None, **kwargs):
        """Resolve an incident (ex: .snooze <ID>)."""
        self.api_headers["From"] = self._find_user(message.source)

        data = {
            "incidents": [{
                "id": params,
                "type": "incident",
                "status": "resolved"
            }]
        }

        url = "%s/incidents" % self.endpoint
        req = request.put(url, headers=self.api_headers, json=data)

        if request.ok(req):
            message.dispatch("Resolved.")
        else:
            message.dispatch("Unable to resolve: %d" % req.status_code)
            message.dispatch(req.text)

    @plugin.hook_add_command("note")
    @utils.require_params
    @utils.spawn
    def note(self, message, params=None, **kwargs):
        """Create a note for an incident (ex: .note <ID> <message>)."""
        params = params.split(" ")
        incident_id = params.pop(0)

        self.api_headers["From"] = self._find_user(message.source)
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
            notes = req.json()["notes"]
            message.dispatch("There are %d notes." % len(notes))

            for note in notes:
                message.dispatch("%s %s - %s" % (note["created_at"],
                                                 note["user"]["summary"],
                                                 note["content"]))
        else:
            message.dispatch("Unable to fetch notes: %d" % req.status_code)
            message.dispatch(req.text)

    @plugin.hook_add_command("oncall")
    @utils.spawn
    def oncall(self, message, params=None, **kwargs):
        """Show who is on call (ex: .oncall)."""
        url = "%s/oncalls" % self.endpoint
        req = request.get(url, headers=self.api_headers)

        if request.ok(req):
            on_calls = []

            for policy in req.json()["oncalls"]:
                if policy["schedule"]:
                    on_calls.append("%s (%s)" % (policy["schedule"]["summary"],
                                                 policy["user"]["summary"]))
            message.dispatch(", ".join(on_calls))
        else:
            message.dispatch("Unable to fetch list: %d" % req.status_code)
            message.dispatch(req.text)

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

    @plugin.hook_add_command("services")
    @utils.spawn
    def services(self, message, params=None, **kwargs):
        """List PagerDuty services (ex: .services)."""
        url = "%s/services?&include[]=integrations&limit=100" % self.endpoint
        req = request.get(url, headers=self.api_headers)

        if request.ok(req):
            for service in req.json()["services"]:
                try:
                    integration = service["integrations"][0]
                    integration_key = integration["integration_key"]
                    message.dispatch("%s (%s)" % (service["summary"],
                                                  integration_key))
                except KeyError:
                    continue
        else:
            message.dispatch("Unable to fetch services: %d" % req.status_code)
            message.dispatch(req.text)

    @plugin.hook_add_command("alert")
    @utils.require_params
    @utils.spawn
    def alert(self, message, params=None, **kwargs):
        """Trigger a custom alert (ex: .alert <service_key> <description>."""
        params = params.split(" ")
        service_key = params.pop(0)
        description = " ".join(params)

        data = {
            "service_key": service_key,
            "event_type": "trigger",
            "description": description,
            "details": description,
            "client": "pyhole %s" % version.version(),
            "client_url": "https://github.com/jk0/pyhole"
        }

        events_host = "https://events.pagerduty.com/"
        url = "%s/generic/2010-04-15/create_event.json" % events_host
        req = request.post(url, headers=self.api_headers, json=data)

        if request.ok(req):
            message.dispatch("Triggered.")
        else:
            message.dispatch("Unable to trigger alert: %d" % req.status_code)
            message.dispatch(req.text)

    def _find_user(self, name):
        """Find a PagerDuty user account."""
        users = self._find_users(name)

        if len(users["users"]) < 1:
            return name

        return users["users"][0]["email"]

    def _find_users(self, name):
        """Find PagerDuty user accounts."""
        url = "%s/users?query=%s&include[]=contact_methods" % (self.endpoint,
                                                               name)
        req = request.get(url, headers=self.api_headers)

        if request.ok(req):
            return req.json()
