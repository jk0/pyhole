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

"""RESTful API Endpoint"""

import flask
import os
import uuid
import sys

import utils
import version


APP = flask.Flask(__name__)


@APP.route("/", methods=["GET"])
def index():
    """Handle index requests."""
    return version.version_string(), 200


# BEGIN PASTE API
@APP.route("/pastes/<paste_id>", methods=["GET"])
def get_paste(paste_id):
    """Fetch and return a paste."""
    paste = utils.read_file("pastes", paste_id)

    if not paste:
        flask.abort(404)

    return flask.Response(paste, status=200, mimetype="text/plain")


@APP.route("/pastes", methods=["POST"])
def create_paste():
    """Create a new paste."""
    request = flask.request.get_json()

    try:
        # NOTE(jk0): We expect all of these keys to exist to be considered a
        # valid paste. Ignore all others.
        data = request["content"]
    except KeyError:
        flask.abort(422)

    file_name = str(uuid.uuid4()).replace("-", "")
    utils.write_file("pastes", file_name, data)

    return flask.redirect("%s/%s" % (flask.request.url, file_name))
# END PASTE API


@utils.subprocess
def run():
    """Run the flask process."""
    config = utils.get_config()

    ssl_crt = config.get("api_ssl_crt", default="")
    ssl_key = config.get("api_ssl_key", default="")

    try:
        if os.path.exists(ssl_crt) and os.path.exists(ssl_key):
            APP.run(host="0.0.0.0", ssl_context=(ssl_crt, ssl_key))
        else:
            APP.run(host="0.0.0.0")
    except KeyboardInterrupt:
        sys.exit(0)
