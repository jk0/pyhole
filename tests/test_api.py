# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from pyhole.core import api, version


def test_index() -> None:
    client = api.APP.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert version.version() in response.get_data(as_text=True)


def test_send_message_requires_fields(pyhole_home) -> None:
    client = api.APP.test_client()
    response = client.post("/messages/send", json={"network": "x"})
    assert response.status_code == 422
