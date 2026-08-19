# Copyright 2016-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole HTTP API (pastebin + optional PagerDuty views)."""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

import flask

from pyhole.core import queue, request, utils, version

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
APP = flask.Flask("pyhole", template_folder=str(TEMPLATE_DIR))
QUEUE = queue.MessageQueue()


def _require_api_auth() -> None:
    token = utils.get_config().get("api_auth_token", default="")
    if not token:
        return
    header = flask.request.headers.get("Authorization", "")
    if header != f"Bearer {token}":
        flask.abort(401)


def _pagerduty_headers() -> dict[str, str]:
    pagerduty = utils.get_config("PagerDuty")
    api_token = pagerduty.get("api_token", default="")
    if not api_token:
        flask.abort(503)
    return {
        "Accept": "application/vnd.pagerduty+json;version=2",
        "Authorization": f"Token token={api_token}",
        "Content-Type": "application/json",
    }


@APP.route("/", methods=["GET"])
def index() -> tuple[str, int]:
    return version.version_string(), 200


@APP.route("/messages/send", methods=["POST"])
def send_message() -> tuple[str, int]:
    _require_api_auth()
    payload = flask.request.get_json(silent=True) or {}
    try:
        item = (payload["network"], payload["target"], payload["message"])
    except KeyError:
        flask.abort(422)
    QUEUE.put(item)
    return str(item), 200


@APP.route("/pagerduty", methods=["GET"])
def get_services() -> str:
    _require_api_auth()
    url = "https://api.pagerduty.com/services?limit=100"
    req = request.get(url, headers=_pagerduty_headers())
    if not request.ok(req):
        flask.abort(req.status_code)
    return flask.render_template(
        "pagerduty_services.html",
        services=req.json()["services"],
        version=version.version_string(),
    )


@APP.route("/pagerduty/incidents/<service_id>", methods=["GET"])
def get_incidents(service_id: str) -> str:
    _require_api_auth()
    url = f"https://api.pagerduty.com/incidents?service_ids[]={service_id}"
    req = request.get(url, headers=_pagerduty_headers())
    if not request.ok(req):
        flask.abort(req.status_code)
    return flask.render_template(
        "pagerduty_incidents.html",
        incidents=req.json()["incidents"],
        version=version.version_string(),
    )


@APP.route("/pagerduty/notes/<incident_id>", methods=["GET"])
def get_notes(incident_id: str) -> str:
    _require_api_auth()
    url = f"https://api.pagerduty.com/incidents/{incident_id}/notes"
    req = request.get(url, headers=_pagerduty_headers())
    if not request.ok(req):
        flask.abort(req.status_code)
    return flask.render_template(
        "pagerduty_notes.html",
        notes=req.json()["notes"],
        version=version.version_string(),
    )


@APP.route("/pastes/<paste_id>", methods=["GET"])
@APP.route("/pastes/<paste_id>/<raw>", methods=["GET"])
def get_paste(paste_id: str, raw: str | None = None) -> flask.Response | str:
    paste_path = utils.get_directory("pastes") / paste_id
    try:
        stats = os.stat(paste_path)
    except OSError:
        flask.abort(404)
    paste = utils.read_file("pastes", paste_id)
    if paste is None:
        flask.abort(404)
    if raw:
        return flask.Response(paste, status=200, mimetype="text/plain")
    return flask.render_template(
        "paste.html",
        paste_id=paste_id,
        paste=paste,
        st_mtime=time.ctime(stats.st_mtime),
        st_size=stats.st_size,
        version=version.version_string(),
    )


@APP.route("/pastes", methods=["POST"])
def create_paste() -> flask.Response:
    _require_api_auth()
    payload = flask.request.get_json(silent=True) or {}
    try:
        paste = payload["paste"]
    except KeyError:
        flask.abort(422)

    file_name = uuid.uuid4().hex
    utils.write_file("pastes", file_name, paste)
    response_url = f"{flask.request.url}/{file_name}"

    network = payload.get("network")
    target = payload.get("target")
    if network and target:
        QUEUE.put((network, target, response_url))

    return flask.redirect(response_url)


@utils.spawn
def run() -> None:
    conf = utils.get_config()
    kwargs: dict = {
        "host": conf.get("api_host", default="127.0.0.1"),
        "port": conf.get("api_port", type="int", default=5000),
        "threaded": True,
    }
    ssl_crt = conf.get("api_ssl_crt", default="")
    ssl_key = conf.get("api_ssl_key", default="")
    if ssl_crt and ssl_key and os.path.exists(ssl_crt) and os.path.exists(ssl_key):
        kwargs["ssl_context"] = (ssl_crt, ssl_key)
    APP.run(**kwargs)
