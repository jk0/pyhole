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

"""Pyhole RESTful API"""

import cgi
import flask
import os
import time
import uuid

from pyhole.core import queue
from pyhole.core import request
from pyhole.core import utils
from pyhole.core import version


APP = flask.Flask("pyhole")
QUEUE = queue.MessageQueue()


@APP.route("/", methods=["GET"])
def index():
    """Handle index requests."""
    return version.version_string(), 200


# BEGIN MESSAGE API #
@APP.route("/messages/send", methods=["POST"])
def send_message():
    """Send a message."""
    request = flask.request.get_json()

    try:
        item = (
            request["network"],
            request["target"],
            request["message"]
        )
    except KeyError:
        flask.abort(422)

    # NOTE(jk0): Disable until auth is implemented.
    # QUEUE.put(item)

    return str(item), 200
# END MESSAGE API #


# BEGIN PAGERDUTY API #
pagerduty = utils.get_config("PagerDuty")
api_token = pagerduty.get("api_token")
api_endpoint = "https://api.pagerduty.com"

api_headers = {
    "Accept": "application/vnd.pagerduty+json;version=2",
    "Authorization": "Token token=%s" % api_token,
    "Content-Type": "application/json"
}


@APP.route("/pagerduty", methods=["GET"])
def get_services():
    """Fetch and return PagerDuty services."""
    url = "%s/services?limit=100" % api_endpoint
    req = request.get(url, headers=api_headers)

    if not request.ok(req):
        flask.abort(req.status_code)

    return flask.render_template(
        "pagerduty_services.html",
        services=req.json()["services"],
        version=version.version_string())


@APP.route("/pagerduty/incidents/<service_id>", methods=["GET"])
def get_incidents(service_id):
    """Fetch and return PagerDuty incidents."""
    url = "%s/incidents?service_ids[]=%s" % (api_endpoint, service_id)
    req = request.get(url, headers=api_headers)

    if not request.ok(req):
        flask.abort(req.status_code)

    return flask.render_template(
        "pagerduty_incidents.html",
        incidents=req.json()["incidents"],
        version=version.version_string())


@APP.route("/pagerduty/notes/<incident_id>", methods=["GET"])
def get_notes(incident_id):
    """Fetch and return PagerDuty notes."""
    url = "%s/incidents/%s/notes" % (api_endpoint, incident_id)
    req = request.get(url, headers=api_headers)

    if not request.ok(req):
        flask.abort(req.status_code)

    return flask.render_template(
        "pagerduty_notes.html",
        notes=req.json()["notes"],
        version=version.version_string())
# END PAGERDUTY API #


# BEGIN PASTE API #
@APP.route("/pastes/<paste_id>", methods=["GET"])
@APP.route("/pastes/<paste_id>/<raw>", methods=["GET"])
def get_paste(paste_id, raw=None):
    """Fetch and return a paste."""
    stats = os.stat(utils.get_directory("pastes") + paste_id)
    st_mtime = time.ctime(stats.st_mtime)
    st_size = stats.st_size

    paste = utils.read_file("pastes", paste_id)

    if not paste:
        flask.abort(404)

    if raw:
        return flask.Response(paste, status=200, mimetype="text/plain")

    return flask.render_template(
        "paste.html",
        paste_id=paste_id,
        paste=cgi.escape(paste),
        st_mtime=st_mtime,
        st_size=st_size,
        version=version.version_string())


@APP.route("/pastes", methods=["POST"])
def create_paste():
    """Create a new paste."""
    try:
        paste = flask.request.get_json()["paste"]
    except KeyError:
        flask.abort(422)

    file_name = str(uuid.uuid4()).replace("-", "")
    utils.write_file("pastes", file_name, paste)

    response = "%s/%s" % (flask.request.url, file_name)

    try:
        # NOTE(jk0): If these items exist, write them to the queue.
        item = (
            flask.request.get_json()["network"],
            flask.request.get_json()["target"],
            response
        )

        QUEUE.put(item)
    except KeyError:
        pass

    return flask.redirect(response)
# END PASTE API #


@utils.spawn
def run():
    """Run the flask process."""
    config = utils.get_config()

    kwargs = {
        "host": "0.0.0.0",
        "threaded": True
    }

    ssl_crt = config.get("api_ssl_crt", default="")
    ssl_key = config.get("api_ssl_key", default="")

    if os.path.exists(ssl_crt) and os.path.exists(ssl_key):
        kwargs["ssl_context"] = (ssl_crt, ssl_key)

    APP.run(**kwargs)
