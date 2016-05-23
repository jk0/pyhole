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

import time

from pyhole.core import plugin
from pyhole.core import request
from pyhole.core import utils


class Ops(plugin.Plugin):
    """Manage operational responsibilities."""

    def __init__(self, session):
        self.session = session
        self.name = self.__class__.__name__

        pagerduty = utils.get_config("PagerDuty")
        self.subdomain = pagerduty.get("subdomain")
        self.api_key = pagerduty.get("api_key")
        self.integration_key = pagerduty.get("integration_key")

        self.api_headers = {
            "Authorization": "Token token=%s" % self.api_key,
            "Content-Type": "application/json"
        }
        self.user_cache = None
        self.reset_current_incident()

    @plugin.hook_add_command("oncall")
    @utils.spawn
    def oncall(self, message, params=None, **kwargs):
        """Show who is on call (ex: .oncall [<group>])."""
        url = "%s/api/v1/escalation_policies/on_call" % self.subdomain
        req = request.get(url, headers=self.api_headers,
                          params={"query": params})

        if request.ok(req):
            response_json = req.json()
            for policy in response_json["escalation_policies"]:
                message.dispatch(policy["name"])

                for level in policy["on_call"]:
                    message.dispatch("- Level %s: %s <%s>" % (
                                     level["level"],
                                     level["user"]["name"],
                                     level["user"]["email"]))
                # NOTE(jk0): This is needed to prevent rate-limiting.
                time.sleep(2)
        else:
            message.dispatch("Unable to fetch list: %d" % req.status_code)

    @plugin.hook_add_command("incident")
    @utils.require_params
    @utils.spawn
    def incident(self, message, params=None, **kwargs):
        """Manage incidents (ex: .incident <create|resolve|setkey>)."""
        param_split = params.split(" ")
        command = param_split.pop(0)
        if command == "create":
            description = " ".join(param_split)
            self.create_incident(message, description)
        elif command == "resolve":
            self.resolve_incident(message)
        elif command == "setkey":
            key = " ".join(param_split)
            self.set_key(message, key)

    @plugin.hook_add_command("note")
    @utils.require_params
    @utils.spawn
    def note(self, message, params=None, **kwargs):
        """Create a note for the current incident (ex: .note <message>)."""
        number = self.get_incident_number()
        if number is None:
            msg = "Could not get incident number for current incident."
            message.dispatch(msg)
            return

        url = "%s/api/v1/incidents/%s/notes" % (self.subdomain, number)
        user = self.find_user_like(message.source)
        if user is None:
            message.dispatch("Could not find PagerDuty user matching: %s" %
                             message.source)
            return

        data = {
            "note": {
                "content": params
            },
            "requester_id": user["id"]
        }

        req = request.post(url, headers=self.api_headers, json=data)

        if request.ok(req):
            message.dispatch("Noted.")
        else:
            message.dispatch("Unable to create note: %d" % req.status_code)
            message.dispatch(req.text)

    @plugin.hook_add_command("notes")
    @utils.spawn
    def notes(self, message, params=None, **kwargs):
        """List all notes in current incident."""
        number = self.get_incident_number()
        if number is None:
            msg = "Could not get incident number for current incident."
            message.dispatch(msg)
            return

        url = "%s/api/v1/incidents/%s/notes" % (self.subdomain, number)
        req = request.get(url, headers=self.api_headers)
        if request.ok(req):
            response_json = req.json()
            notes = response_json["notes"]
            message.dispatch("There are %d notes." % len(notes))

            for note in notes:
                message.dispatch("%s %s - %s" % (note["created_at"],
                                                 note["user"]["name"],
                                                 note["content"]))
        else:
            message.dispatch("Unable to fetch notes: %d" % req.status_code)

    def create_incident(self, message, description):
        """Create a PagerDuty incident with specified description."""
        # would have been called url, but flake8 complains that line is 81 long
        u = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
        data = {
            "service_key": self.integration_key,
            "event_type": "trigger",
            "description": description,
            "incident_key": utils.datetime_now_string(),
            "details": {"triggered by": message.source}
        }

        req = request.post(u, json=data)
        response_json = req.json()
        if request.ok(req):
            self.set_incident_key(response_json["incident_key"])
            message.dispatch("Created incident with incident_key: %s" %
                             self.get_incident_key())
        else:
            message.dispatch("Error creating incident: %d" % req.status_code)
            message.dispatch(response_json["message"])

    def resolve_incident(self, message):
        """Close the current PagerDuty incident."""
        incident_id = self.get_incident_id()
        if incident_id is None:
            message.dispatch("Could not find ID for current incident.")
            return

        url = "%s/api/v1/incidents/%s/resolve" % (self.subdomain, incident_id)
        user = self.find_user_like(message.source)
        if user is None:
            message.dispatch("Could not find PagerDuty user: %s" %
                             message.source)
            return

        data = {"requester_id": user["id"]}

        req = request.put(url, headers=self.api_headers, json=data)

        if request.ok(req):
            self.reset_current_incident()
            message.dispatch("Resolved incident successfully.")
        else:
            message.dispatch("Could not resolve incident: %d" %
                             req.status_code)
            message.dispatch(req.text)

    def set_key(self, message, key):
        """Set the current incident key."""
        self.set_incident_key(key)
        message.dispatch("Key set to: %s" % key)

    def get_users(self):
        """Get PagerDuty users and fill the cache."""
        url = "%s/api/v1/users" % self.subdomain
        req = request.get(url, headers=self.api_headers)
        if request.ok(req):
            response_json = req.json()
            return response_json["users"]
        else:
            return None

    def find_user_like(self, query):
        """Finds a PagerDuty user matching the query (name/email)."""
        # if cache is empty, fill it
        if self.user_cache is None:
            self.user_cache = self.get_users()

        # if it's still empty, something's wrong
        if self.user_cache is not None:
            # search the names first
            for user in self.user_cache:
                if query in user["name"]:
                    return user
            # then search the emails
            for user in self.user_cache:
                if query in user["email"]:
                    return user
        return None

    def reset_current_incident(self):
        """Resets the current incident state."""
        self.current_incident = {
            "key": None,
            "number": None,
            "id": None
        }

    def get_incident_key(self):
        return self.current_incident["key"]

    def get_incident_number(self):
        number = self.current_incident["number"]
        if number is None:
            number = self.find_incident_number()
            self.set_incident_number(number)
        return number

    def get_incident_id(self):
        the_id = self.current_incident["id"]
        if the_id is None:
            new_id = self.find_incident_id()
            self.set_incident_id(new_id)
        return the_id

    def set_incident_key(self, key):
        self.current_incident["key"] = key

    def set_incident_number(self, number):
        self.current_incident["number"] = number

    def set_incident_id(self, new_id):
        self.current_incident["id"] = new_id

    def find_incident_number(self):
        """Finds incident number from the current incident key."""
        key = self.get_incident_key()
        if key is not None:
            url = "%s/api/v1/incidents" % self.subdomain
            params = {"incident_key": key, "sort_by": "created_on:desc"}
            req = request.get(url, headers=self.api_headers, params=params)

            if request.ok(req):
                response_json = req.json()
                incidents = response_json["incidents"]
                if len(incidents) > 0:
                    number = incidents[0]["incident_number"]
                    return number
        return None

    def find_incident_id(self):
        """Finds incident id from the current incident number."""
        number = self.get_incident_number()
        if number is not None:
            url = "%s/api/v1/incidents/%s" % (self.subdomain, number)
            req = request.get(url, headers=self.api_headers)
            if request.ok(req):
                response_json = req.json()
                return response_json["id"]
        return None
