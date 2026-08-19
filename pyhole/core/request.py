# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole HTTP client."""

from __future__ import annotations

from typing import Any

import requests

from pyhole.core import version

DEFAULT_TIMEOUT = 15

session = requests.Session()
session.headers.update({"User-Agent": f"pyhole/{version.version()}"})


def get(url: str, **kwargs: Any) -> requests.Response:
    """GET a URL with a default timeout."""
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    return session.get(url, **kwargs)


def post(url: str, **kwargs: Any) -> requests.Response:
    """POST to a URL with a default timeout."""
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    return session.post(url, **kwargs)


def put(url: str, **kwargs: Any) -> requests.Response:
    """PUT to a URL with a default timeout."""
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    return session.put(url, **kwargs)


def ok(response: requests.Response) -> bool:
    """Check if a response is 2xx."""
    return 200 <= response.status_code < 300
