# Copyright 2011-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

from pyhole.core import version


def test_version_string() -> None:
    assert version.version_string().startswith("pyhole v")


def test_version() -> None:
    assert version.version() == "1.0.0"


def test_version_hash() -> None:
    assert version.version_hash().startswith("1.0.0")
