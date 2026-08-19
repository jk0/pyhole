# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole version handling."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

__VERSION__ = "1.0.0"
_REPO_ROOT = Path(__file__).resolve().parents[2]


def current_git_hash() -> str | None:
    """Return a short git hash for this checkout, if available."""
    git = shutil.which("git")
    if git is None or not (_REPO_ROOT / ".git").exists():
        return None
    try:
        result = subprocess.run(
            [git, "-C", str(_REPO_ROOT), "rev-parse", "--short=7", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def version_string() -> str:
    """Return the human-readable version banner."""
    git_hash = current_git_hash()
    if git_hash:
        return f"pyhole v{__VERSION__} ({git_hash}) - https://github.com/jk0/pyhole"
    return f"pyhole v{__VERSION__} - https://github.com/jk0/pyhole"


def version_hash() -> str:
    """Return version plus git hash, if known."""
    git_hash = current_git_hash()
    if git_hash:
        return f"{__VERSION__}-{git_hash}"
    return __VERSION__


def version() -> str:
    """Return the current version."""
    return __VERSION__
