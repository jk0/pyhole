# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace

from pyhole.plugins import kernel
from tests.conftest import FakeMessage, FakeSession, call_unwrapped


def test_kernel(monkeypatch, clean_plugins) -> None:
    banner = "The latest stable version of the Linux kernel is:        6.8.1\nThe latest mainline version of the Linux kernel is:      6.9-rc4\n"

    monkeypatch.setattr(
        "pyhole.plugins.kernel.request.get",
        lambda url, **kwargs: SimpleNamespace(text=banner, status_code=200),
    )
    session = FakeSession()
    plugin_obj = kernel.Kernel(session)
    message = FakeMessage(session, ".kernel")
    call_unwrapped(plugin_obj.kernel, plugin_obj, message)
    assert message.dispatched
    assert "mainline" in message.dispatched[0]
