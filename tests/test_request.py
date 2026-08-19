# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

from pyhole.core import request


def test_ok() -> None:
    assert request.ok(SimpleNamespace(status_code=200))
    assert request.ok(SimpleNamespace(status_code=201))
    assert not request.ok(SimpleNamespace(status_code=404))
    assert not request.ok(SimpleNamespace(status_code=500))


def test_user_agent() -> None:
    assert "pyhole/" in request.session.headers["User-Agent"]
