# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole utilities."""

from __future__ import annotations

import argparse
import functools
import os
import re
import shutil
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from html import unescape
from importlib import resources
from pathlib import Path
from typing import Any, TypeVar

from bs4 import BeautifulSoup

from pyhole.core import config, version

F = TypeVar("F", bound=Callable[..., Any])

_CLI_ARGS: argparse.Namespace | None = None


def admin(func: F) -> F:
    """Require admin rights."""

    @functools.wraps(func)
    def wrap(self: Any, message: Any, *args: Any, **kwargs: Any) -> Any:
        if message.source in self.session.admins:
            return func(self, message, *args, **kwargs)
        return message.dispatch("Sorry, you are not authorized to do that.")

    return wrap  # type: ignore[return-value]


def require_params(func: F) -> F:
    """Require parameters."""

    @functools.wraps(func)
    def wrap(self: Any, message: Any, params: str | None, *args: Any, **kwargs: Any) -> Any:
        if not params:
            message.dispatch(wrap.__doc__)
            return None
        return func(self, message, params, *args, **kwargs)

    return wrap  # type: ignore[return-value]


def spawn(func: F) -> F:
    """Run the wrapped function in a daemon thread."""

    @functools.wraps(func)
    def wrap(*args: Any, **kwargs: Any) -> None:
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()

    return wrap  # type: ignore[return-value]


def decode_entities(html: str) -> str:
    """Strip HTML tags/entities and keep printable ASCII."""
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    text = unescape(text)
    return "".join(ch for ch in text if 9 < ord(ch) < 127)


def ensure_int(param: str | None) -> int | None:
    """Ensure the given param is an int, stripping non-word characters."""
    if param is None:
        return None
    try:
        return int(re.sub(r"\W", "", param))
    except ValueError:
        return None


def build_options(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line options."""
    parser = argparse.ArgumentParser(prog="pyhole", description="A modular IRC and Slack bot.")
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="path to a configuration file",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="show debugging output")
    parser.add_argument("-V", "--version", action="version", version=version.version_string())
    return parser.parse_args(argv)


def set_cli_args(args: argparse.Namespace) -> None:
    """Record parsed CLI args so helpers do not re-parse sys.argv."""
    global _CLI_ARGS
    _CLI_ARGS = args


def get_option(option: str) -> Any:
    """Retrieve an option from the command line."""
    global _CLI_ARGS
    if _CLI_ARGS is None:
        _CLI_ARGS = build_options([])
    return getattr(_CLI_ARGS, option, None)


def debug_enabled() -> bool:
    """Return whether debug mode is enabled."""
    if get_option("debug"):
        return True
    try:
        return bool(get_config().get("debug", type="bool", default=False))
    except config.ConfigError:
        return False


def get_home_directory() -> Path:
    """Return the pyhole home directory, creating it if needed."""
    env_home = os.environ.get("PYHOLE_HOME")
    home = Path(env_home).expanduser() if env_home else Path.home() / ".pyhole"
    make_directory(home)
    return home


def get_directory(new_dir: str) -> Path:
    """Return a subdirectory of the pyhole home directory."""
    path = get_home_directory() / new_dir
    make_directory(path)
    return path


def make_directory(directory: str | Path) -> Path:
    """Make a directory if it does not exist."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_conf_file_path() -> Path:
    """Return the default path to the conf file."""
    for path in (Path("/etc/pyhole.conf"), Path("/etc/pyhole/pyhole.conf")):
        if path.is_file():
            return path
    return get_home_directory() / "pyhole.conf"


def get_conf_file() -> Path:
    """Return the path to the conf file, honoring --config."""
    cli = get_option("config")
    if cli:
        return Path(cli).expanduser()
    return get_conf_file_path()


def get_config(section: str = "Pyhole") -> config.Config:
    """Return a Config object for ``section``."""
    return config.Config(get_conf_file(), section)


def write_file(directory: str, file_name: str, data: Any) -> Path:
    """Write data to a file under the pyhole home directory."""
    path = get_directory(directory) / file_name
    path.write_text(str(data).strip(), encoding="utf-8")
    return path


def read_file(directory: str, file_name: str) -> str | None:
    """Read a file under the pyhole home directory."""
    path = get_directory(directory) / file_name
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def list_files(directory: str) -> list[str]:
    """List files in a directory under the pyhole home directory."""
    path = get_directory(directory)
    return [entry.name for entry in path.iterdir() if entry.is_file()]


def sample_config_path() -> Path | None:
    """Return the packaged sample config, if it can be located."""
    try:
        ref = resources.files("pyhole.data").joinpath("pyhole.conf.sample")
        with resources.as_file(ref) as path:
            if path.is_file():
                return path
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        pass
    repo_sample = Path(__file__).resolve().parents[2] / "pyhole.conf.sample"
    if repo_sample.is_file():
        return repo_sample
    return None


def prepare_config() -> bool:
    """Copy a sample configuration file into place if missing.

    Returns True if a new file was written.
    """
    conf_file = get_conf_file()
    if conf_file.exists():
        return False
    sample = sample_config_path()
    if sample is None:
        return False
    make_directory(conf_file.parent)
    shutil.copyfile(sample, conf_file)
    print(f"Copied sample configuration file to: {conf_file}")
    print("Please edit it before running again.")
    return True


def datetime_now_string() -> str:
    """ISO 8601 UTC timestamp."""
    return datetime.now(UTC).isoformat()
