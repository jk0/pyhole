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

import re
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

        self.api_headers = {
            "Authorization": "Token token=%s" % self.api_key,
            "Content-Type": "application/json"
        }
        self.user_cache = None

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

    @plugin.hook_add_command("note")
    @utils.require_params
    @utils.spawn
    def note(self, message, params=None, **kwargs):
        """Create a note for an incident (ex: .note <ID> <message>)."""
        params = params.split(" ")
        incident_id = params.pop(0)

        url = "%s/api/v1/incidents/%s/notes" % (self.subdomain, incident_id)
        user = self.find_user_like(message.source)
        if user is None:
            message.dispatch("Could not find PagerDuty user matching: %s" %
                             message.source)
            return

        data = {
            "requester_id": user["id"],
            "note": {
                "content": " ".join(params)
            }
        }

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
        url = "%s/api/v1/incidents/%s/notes" % (self.subdomain, params)
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

    @plugin.hook_add_command("lookup")
    @utils.require_params
    @utils.spawn
    def lookup(self, message, params=None, **kwargs):
        """Lookup user's phone numbers (ex: .lookup <name>."""
        url = "%s/api/v1/users?include[]=contact_methods&limit=100" % (
            self.subdomain)
        response = request.get(url, headers=self.api_headers).json()
        results = []
        for user in response["users"]:
            found_user = re.search(params, user["name"], re.IGNORECASE)
            found_email = re.search(params, user["email"], re.IGNORECASE)
            if found_user or found_email:
                for contact in user["contact_methods"]:
                    if contact["type"] == "phone":
                        results.append("%s (%s)" % (user["name"],
                                                    contact["phone_number"]))
        if len(results) > 0:
            message.dispatch(", ".join(results))
        else:
            message.dispatch("No results found: %s" % params)

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
