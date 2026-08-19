# Copyright 2016-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""PagerDuty operations plugin."""

from __future__ import annotations

from pyhole.core import plugin, request, utils, version


class Ops(plugin.Plugin):
    """PagerDuty incident tools."""

    def __init__(self, session):
        super().__init__(session)
        pagerduty = utils.get_config("PagerDuty")
        self.api_token = pagerduty.get("api_token")
        self.endpoint = "https://api.pagerduty.com"
        self.api_headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": f"Token token={self.api_token}",
            "Content-Type": "application/json",
        }

    @plugin.hook_add_command("query")
    @utils.require_params
    @utils.spawn
    def query(self, message, params=None, **kwargs):
        """Query an incident (ex: .query <ID>)."""
        req = request.get(f"{self.endpoint}/incidents/{params}", headers=self.api_headers)
        if request.ok(req):
            incident = req.json()["incident"]
            message.dispatch(
                f"{incident['summary']} [{incident['status']}]: {incident['html_url']}"
            )
        else:
            message.dispatch(f"Unable to query incident: {req.status_code}")
            message.dispatch(req.text)

    @plugin.hook_add_command("ack")
    @utils.require_params
    @utils.spawn
    def ack(self, message, params=None, **kwargs):
        """Acknowledge an incident (ex: .ack <ID>)."""
        self._set_status(message, params, "acknowledged", "Acknowledged.")

    @plugin.hook_add_command("resolve")
    @utils.require_params
    @utils.spawn
    def resolve(self, message, params=None, **kwargs):
        """Resolve an incident (ex: .resolve <ID>)."""
        self._set_status(message, params, "resolved", "Resolved.")

    def _set_status(self, message, incident_id: str, status: str, ok_text: str) -> None:
        headers = {**self.api_headers, "From": self._find_user(message.source)}
        data = {"incidents": [{"id": incident_id, "type": "incident", "status": status}]}
        req = request.put(f"{self.endpoint}/incidents", headers=headers, json=data)
        if request.ok(req):
            message.dispatch(ok_text)
        else:
            message.dispatch(f"Unable to update incident: {req.status_code}")
            message.dispatch(req.text)

    @plugin.hook_add_command("note")
    @utils.require_params
    @utils.spawn
    def note(self, message, params=None, **kwargs):
        """Create a note for an incident (ex: .note <ID> <message>)."""
        incident_id, _, content = params.partition(" ")
        headers = {**self.api_headers, "From": self._find_user(message.source)}
        req = request.post(
            f"{self.endpoint}/incidents/{incident_id}/notes",
            headers=headers,
            json={"note": {"content": content}},
        )
        if request.ok(req):
            message.dispatch("Noted.")
        else:
            message.dispatch(f"Unable to create note: {req.status_code}")
            message.dispatch(req.text)

    @plugin.hook_add_command("notes")
    @utils.require_params
    @utils.spawn
    def notes(self, message, params=None, **kwargs):
        """List notes on an incident (ex: .notes <ID>)."""
        req = request.get(f"{self.endpoint}/incidents/{params}/notes", headers=self.api_headers)
        if not request.ok(req):
            message.dispatch(f"Unable to fetch notes: {req.status_code}")
            message.dispatch(req.text)
            return
        notes = req.json()["notes"]
        message.dispatch(f"There are {len(notes)} notes.")
        for note in notes:
            message.dispatch(f"{note['created_at']} {note['user']['summary']} - {note['content']}")

    @plugin.hook_add_command("oncall")
    @utils.spawn
    def oncall(self, message, params=None, **kwargs):
        """Show who is on call (ex: .oncall)."""
        req = request.get(f"{self.endpoint}/oncalls", headers=self.api_headers)
        if not request.ok(req):
            message.dispatch(f"Unable to fetch list: {req.status_code}")
            message.dispatch(req.text)
            return
        on_calls = []
        for policy in req.json()["oncalls"]:
            if policy.get("schedule"):
                on_calls.append(f"{policy['schedule']['summary']} ({policy['user']['summary']})")
        message.dispatch(", ".join(on_calls) if on_calls else "Nobody is on call.")

    @plugin.hook_add_command("lookup")
    @utils.require_params
    @utils.spawn
    def lookup(self, message, params=None, **kwargs):
        """Lookup a user's phone numbers (ex: .lookup <name>)."""
        users = self._find_users(params)
        results = []
        for user in users.get("users", []):
            for contact in user.get("contact_methods", []):
                if contact.get("type") == "phone_contact_method":
                    results.append(f"{user['name']} ({contact['address']})")
        message.dispatch(", ".join(results) if results else f"No results found: {params}")

    @plugin.hook_add_command("services")
    @utils.spawn
    def services(self, message, params=None, **kwargs):
        """List PagerDuty services (ex: .services)."""
        url = f"{self.endpoint}/services?include[]=integrations&limit=100"
        req = request.get(url, headers=self.api_headers)
        if not request.ok(req):
            message.dispatch(f"Unable to fetch services: {req.status_code}")
            message.dispatch(req.text)
            return
        for service in req.json()["services"]:
            try:
                key = service["integrations"][0]["integration_key"]
            except (KeyError, IndexError):
                continue
            message.dispatch(f"{service['summary']} ({key})")

    @plugin.hook_add_command("alert")
    @utils.require_params
    @utils.spawn
    def alert(self, message, params=None, **kwargs):
        """Trigger a custom alert (ex: .alert <service_key> <description>)."""
        service_key, _, description = params.partition(" ")
        data = {
            "service_key": service_key,
            "event_type": "trigger",
            "description": description,
            "details": description,
            "client": f"pyhole {version.version()}",
            "client_url": "https://github.com/jk0/pyhole",
        }
        url = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
        req = request.post(url, headers=self.api_headers, json=data)
        if request.ok(req):
            message.dispatch("Triggered.")
        else:
            message.dispatch(f"Unable to trigger alert: {req.status_code}")
            message.dispatch(req.text)

    def _find_user(self, name: str) -> str:
        users = self._find_users(name).get("users", [])
        if not users:
            return name
        return users[0].get("email", name)

    def _find_users(self, name: str) -> dict:
        url = f"{self.endpoint}/users?query={name}&include[]=contact_methods"
        req = request.get(url, headers=self.api_headers)
        if request.ok(req):
            return req.json()
        return {"users": []}
