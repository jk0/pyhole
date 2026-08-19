# Copyright 2011-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from pyhole.core import config


@pytest.fixture
def sample_config() -> config.Config:
    path = Path(__file__).resolve().parents[1] / "pyhole.conf.sample"
    return config.Config(path, "Pyhole")


def test_missing_parameter_raises(sample_config: config.Config) -> None:
    with pytest.raises(config.ConfigError):
        sample_config.get("foo")


def test_missing_parameter_default(sample_config: config.Config) -> None:
    assert sample_config.get("foo", default="bar") == "bar"


def test_sections(sample_config: config.Config) -> None:
    sections = sample_config.sections()
    assert isinstance(sections, list)
    assert "Pyhole" in sections
    assert "FreeNode" in sections


def test_get_int(sample_config: config.Config) -> None:
    assert sample_config.get("reconnect_delay", type="int") == 60


def test_get_bool(sample_config: config.Config) -> None:
    assert sample_config.get("debug", type="bool") is False


def test_get_list(sample_config: config.Config) -> None:
    admins = sample_config.get("admins", type="list")
    assert isinstance(admins, list)
    assert "nick!ident" in admins


def test_get_str(sample_config: config.Config) -> None:
    assert sample_config.get("command_prefix") == "."


def test_list_split_strips_whitespace(sample_config: config.Config) -> None:
    plugins = sample_config.get("plugins", type="list")
    assert "admin" in plugins
    assert all(item == item.strip() for item in plugins)


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(config.ConfigError):
        config.Config(tmp_path / "nope.conf", "Pyhole")
