# Copyright 2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from pyhole.core import plugin, utils


@pytest.fixture
def pyhole_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("PYHOLE_HOME", str(tmp_path))
    conf = tmp_path / "pyhole.conf"
    sample = Path(__file__).resolve().parents[1] / "pyhole.conf.sample"
    conf.write_text(sample.read_text(encoding="utf-8"), encoding="utf-8")
    utils.set_cli_args(utils.build_options(["-c", str(conf)]))
    return tmp_path


@pytest.fixture
def clean_plugins():
    plugin.Plugin._plugin_classes = []
    plugin._reset_variables()
    yield
    for instance in plugin._plugin_instances:
        instance.stop()
    plugin.Plugin._plugin_classes = []
    plugin._reset_variables()


class FakeSession:
    def __init__(self) -> None:
        self.nick = "pyhole"
        self.addressed = False
        self.command_prefix = "."
        self.admins = ["alice!ident"]
        self.log = logging.getLogger("test")
        self.version = "pyhole v1.0.0"
        self.replies: list[tuple[str, str]] = []

    def reply(self, target: str, msg: str) -> None:
        self.replies.append((target, msg))

    def notice(self, target: str, msg: str) -> None:
        self.replies.append((target, msg))

    def load_plugins(self, reload_plugins: bool = False) -> None:
        if reload_plugins:
            plugin.reload_plugins(session=self)
        else:
            plugin.load_plugins(session=self)

    def op_user(self, params: str) -> None:
        self.replies.append(("op", params))

    def deop_user(self, params: str) -> None:
        self.replies.append(("deop", params))

    def set_nick(self, params: str) -> None:
        self.nick = params

    def join_channel(self, params: str) -> None:
        self.replies.append(("join", params))

    def part_channel(self, params: str) -> None:
        self.replies.append(("part", params))


class FakeMessage:
    def __init__(
        self, session: FakeSession, text: str, source: str = "alice!ident", target: str = "#chan"
    ) -> None:
        self.session = session
        self.message = text
        self.source = source
        self.target = target
        self.dispatched: list[str] = []

    def dispatch(self, reply) -> None:
        self.dispatched.append(str(reply))


def call_unwrapped(method, *args, **kwargs):
    """Call a decorated plugin method without spawn/require_params wrappers."""
    fn = method.__func__ if hasattr(method, "__func__") else method
    while hasattr(fn, "__wrapped__"):
        fn = fn.__wrapped__
    return fn(*args, **kwargs)
