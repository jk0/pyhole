#   Copyright 2016 Patrick Tsai
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

"""Pyhole Request Manager"""

import requests

import version


session = requests.Session()
session.headers.update({
    "User-Agent": "pyhole/%s" % version.version()
})


def get(url, **kwargs):
    """GET a URL."""
    return session.get(url, **kwargs)


def post(url, **kwargs):
    """POST to a URL."""
    return session.post(url, **kwargs)


def put(url, **kwargs):
    """PUT to a URL."""
    return session.put(url, **kwargs)


def ok(request):
    """Check if a request is OK (2xx)."""
    return request.status_code >= 200 and request.status_code < 300
