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


# BEGIN PASTE API #
PASTE_TEMPLATE = """{% set lines = paste.split('\n') %}<html>
<head>
<title>{{ paste_id }} | pyhole</title>
<style type="text/css">
* {
    margin: 0;
    padding: 0;
}
body {
    margin: 20px 0;
    background-color: #fff;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}
pre {
    padding: 10px;
    font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 12px;
    color: #333;
    letter-spacing: 0.5px;
    line-height: 160%;
    white-space: pre-wrap;
}
#paste {
    margin: 0 auto;
    width: 65%;
    border-radius: 3px;
    border: 1px solid #ddd;
}
#lines {
    float: left;
    width: 3%;
    color: #b3b3b3;
    text-align: right;
    border-right: 1px solid #eee;
}
#snippet {
    overflow: auto;
}
#header {
    border-bottom: 1px solid #ddd;
    padding: 15px;
    background-color: #f7f7f7;
    font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-weight: bold;
    font-size: 14px;
    color: #4078c0;
}
#header p {
    float: left;
    width: 94%;
}
#header a {
    padding: 5px 10px;
    border: 1px solid #d5d5d5;
    border-radius: 3px;
    background-color: #f7f7f7;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
    text-decoration: none;
    color: #333;
}
#header a:hover {
    background-color: #e6e6e6;
    border: 1px solid #ccc;
}
#copyright {
    padding: 20px 0 0 0;
    font-size: 12px;
    color: #767676;
    text-align: center;
}
</style>
</head>
<body>
<div id="paste">
<div id="header">
<p>{{ st_mtime }} / {{ st_size }} bytes</p>
<a href="/pastes/{{ paste_id }}/raw">Raw</a>
</div>
<pre id="lines">{% for line in lines %}
{{ loop.index }}{% endfor %}</pre>
<pre id="snippet">{{ paste }}</pre>
</div>
<p id="copyright">{{ version }}</p>
</body>
</html>
"""


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

    return flask.render_template_string(
        PASTE_TEMPLATE,
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
