# Copyright 2011-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from pyhole.core import utils


def test_decode_entities() -> None:
    assert utils.decode_entities("<foo>&#64;&amp;bar&amp;&#64;</foo>") == "@&bar&@"


def test_decode_entities_returns_str() -> None:
    result = utils.decode_entities("hello")
    assert isinstance(result, str)
    assert result == "hello"


def test_ensure_int() -> None:
    assert utils.ensure_int("3") == 3
    assert utils.ensure_int(r"\W") is None
    assert utils.ensure_int("a") is None
    assert utils.ensure_int("-123") == 123
    assert utils.ensure_int(None) is None


def test_build_options() -> None:
    parsed = utils.build_options([])
    assert parsed.debug is False
    assert parsed.config is None


def test_home_directory(pyhole_home) -> None:
    home = utils.get_home_directory()
    assert home == pyhole_home
    assert home.is_dir()


def test_get_directory(pyhole_home) -> None:
    path = utils.get_directory("test_dir")
    assert path == pyhole_home / "test_dir"
    assert path.is_dir()


def test_conf_file(pyhole_home) -> None:
    assert utils.get_conf_file() == pyhole_home / "pyhole.conf"


def test_get_config(pyhole_home) -> None:
    conf = utils.get_config()
    assert conf.get("debug", type="bool") is False


def test_write_and_read_file(pyhole_home) -> None:
    utils.write_file("tests", "pyhole_test_file", "foo")
    assert utils.read_file("tests", "pyhole_test_file") == "foo"
    assert "pyhole_test_file" in utils.list_files("tests")


def test_datetime_now_string() -> None:
    stamp = utils.datetime_now_string()
    assert "T" in stamp
