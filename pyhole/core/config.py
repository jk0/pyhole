# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole configuration manager."""

from __future__ import annotations

import configparser
from pathlib import Path
from typing import Any, Literal, overload

GetType = Literal["str", "int", "bool", "list"]
_MISSING = object()


class ConfigError(Exception):
    """Raised when a required configuration value is missing or invalid."""


class Config:
    """A configuration object for one INI section."""

    def __init__(self, config: str | Path, section: str) -> None:
        self.config = Path(config).expanduser().resolve()
        self.config_parser = configparser.ConfigParser()
        self.section = section
        self._load()

    def _load(self) -> None:
        if not self.config.is_file():
            raise ConfigError(f"Unable to load configuration file: {self.config}")
        with self.config.open(encoding="utf-8") as conf_file:
            self.config_parser.read_file(conf_file)

    def __str__(self) -> str:
        return self.section

    def sections(self) -> list[str]:
        return self.config_parser.sections()

    def has_section(self, section: str) -> bool:
        return self.config_parser.has_section(section)

    @overload
    def get(self, option: str, *, type: Literal["str"] = "str", default: str) -> str: ...
    @overload
    def get(self, option: str, *, type: Literal["int"], default: int) -> int: ...
    @overload
    def get(self, option: str, *, type: Literal["bool"], default: bool) -> bool: ...
    @overload
    def get(self, option: str, *, type: Literal["list"], default: list[str]) -> list[str]: ...
    @overload
    def get(self, option: str, *, type: GetType = "str", default: Any = _MISSING) -> Any: ...

    def get(self, option: str, **kwargs: Any) -> Any:
        """Retrieve a configuration value.

        ``type`` is one of ``str`` (default), ``int``, ``bool``, or ``list``.
        Lists are comma-separated and stripped. Missing options raise
        ConfigError unless ``default`` is provided.
        """
        value_type: GetType = kwargs.get("type", "str")
        default = kwargs.get("default", _MISSING)

        try:
            if value_type == "int":
                return self.config_parser.getint(self.section, option)
            if value_type == "bool":
                return self.config_parser.getboolean(self.section, option)
            raw = self.config_parser.get(self.section, option)
            if value_type == "list":
                if not raw.strip():
                    return []
                return [item.strip() for item in raw.split(",") if item.strip()]
            return raw
        except (configparser.NoOptionError, configparser.NoSectionError):
            if default is not _MISSING:
                return default
            raise ConfigError(
                f"Unable to locate '{option}' in {self.config} [{self.section}]"
            ) from None
        except ValueError as exc:
            raise ConfigError(
                f"Invalid {value_type} for '{option}' in [{self.section}]: {exc}"
            ) from exc
