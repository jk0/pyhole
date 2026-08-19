# Copyright 2011-2026 Chris Behrens, Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole plugin manager."""

from __future__ import annotations

import importlib
import importlib.util
import re
import sys
import threading
import time
from collections.abc import Callable
from typing import Any

from pyhole.core import config, logger, utils

LOG = logger.get_logger()

HookFunc = Callable[..., Any]

_plugin_instances: list[Plugin] = []
_plugin_hooks: dict[str, list[tuple[str, HookFunc, Any]]] = {}
_HOOK_NAMES = ("keyword", "command", "msg_regex", "poll")


def _reset_variables() -> None:
    global _plugin_instances, _plugin_hooks
    _plugin_instances = []
    _plugin_hooks = {name: [] for name in _HOOK_NAMES}


_reset_variables()


def hook_add(hookname: str, arg: Any, poll_timer: int = 60) -> Callable[[HookFunc], HookFunc]:
    """Generic decorator to mark a plugin method as a hook."""

    def decorator(func: HookFunc) -> HookFunc:
        setattr(func, f"_is_{hookname}_hook", True)
        func._hook_arg = arg  # type: ignore[attr-defined]
        func._poll_timer = poll_timer  # type: ignore[attr-defined]
        return func

    return decorator


def hook_add_command(name: str) -> Callable[[HookFunc], HookFunc]:
    return hook_add("command", name)


def hook_add_keyword(name: str) -> Callable[[HookFunc], HookFunc]:
    return hook_add("keyword", name)


def hook_add_msg_regex(pattern: str) -> Callable[[HookFunc], HookFunc]:
    return hook_add("msg_regex", pattern)


def hook_add_poll(name: str, poll_timer: int = 60) -> Callable[[HookFunc], HookFunc]:
    return hook_add("poll", name, poll_timer=poll_timer)


def hook_get(hookname: str) -> list[tuple[str, HookFunc, Any]]:
    return _plugin_hooks[hookname]


def hook_get_commands() -> list[tuple[str, HookFunc, Any]]:
    return hook_get("command")


def hook_get_keywords() -> list[tuple[str, HookFunc, Any]]:
    return hook_get("keyword")


def hook_get_msg_regexes() -> list[tuple[str, HookFunc, Any]]:
    return hook_get("msg_regex")


# Historical misspelling kept so older plugins/docs still work.
hook_get_msg_regexs = hook_get_msg_regexes


def hook_get_polls() -> list[tuple[str, HookFunc, Any]]:
    return hook_get("poll")


def active_get(hookname: str) -> str:
    return ", ".join(sorted(str(item[2]) for item in _plugin_hooks[hookname]))


def active_commands() -> str:
    return active_get("command")


def active_keywords() -> str:
    return active_get("keyword")


def active_msg_regexes() -> str:
    return active_get("msg_regex")


active_msg_regexs = active_msg_regexes


def active_polls() -> str:
    return active_get("poll")


class PluginMetaClass(type):
    """Register Plugin subclasses as they are defined."""

    def __init__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> None:
        super().__init__(name, bases, attrs)
        if name == "Plugin":
            return
        if cls not in Plugin._plugin_classes:
            Plugin._plugin_classes.append(cls)


class Plugin(metaclass=PluginMetaClass):
    """Base class for every plugin."""

    _plugin_classes: list[type[Plugin]] = []

    def __init__(self, session: Any, *args: Any, **kwargs: Any) -> None:
        self.session = session
        self.name = type(self).__name__
        self._stop = threading.Event()

    def stop(self) -> None:
        """Signal poll loops started for this instance to exit."""
        self._stop.set()


def _poll_loop(instance: Plugin, func: HookFunc, timer: int) -> None:
    while not instance._stop.is_set():
        try:
            func(None, None)
        except Exception:
            LOG.exception("Poll %s.%s failed", instance.name, func.__name__)
        if instance._stop.wait(timer):
            return


def _init_plugins(*args: Any, **kwargs: Any) -> None:
    for cls in list(Plugin._plugin_classes):
        try:
            instance = cls(*args, **kwargs)
        except config.ConfigError as exc:
            LOG.warning("Skipping plugin %s: %s", cls.__name__, exc)
            continue
        except Exception:
            LOG.exception("Failed to initialize plugin %s", cls.__name__)
            continue

        _plugin_instances.append(instance)

        for attr_name in dir(instance):
            attr = getattr(instance, attr_name)
            for hook_key in _HOOK_NAMES:
                if not getattr(attr, f"_is_{hook_key}_hook", False):
                    continue
                hook_arg = getattr(attr, "_hook_arg", None)
                _plugin_hooks[hook_key].append((attr.__module__, attr, hook_arg))
                if hook_key == "poll":
                    timer = int(getattr(attr, "_poll_timer", 60))
                    thread = threading.Thread(
                        target=_poll_loop,
                        args=(instance, attr, timer),
                        name=f"poll-{instance.name}-{attr.__name__}",
                        daemon=True,
                    )
                    thread.start()


def _import_user_plugin(plugin_name: str) -> None:
    plugin_dir = utils.get_directory("plugins")
    sys.path.append(str(plugin_dir))
    for entry in plugin_dir.glob("*.py"):
        if entry.stem != plugin_name:
            continue
        spec = importlib.util.spec_from_file_location(plugin_name, entry)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            LOG.exception("Failed to load user plugin %s", plugin_name)


def load_plugins(*args: Any, **kwargs: Any) -> None:
    """Load plugins listed in configuration."""
    conf = utils.get_config()
    plugin_names = conf.get("plugins", type="list", default=["admin"])

    for plugin_name in plugin_names:
        _import_user_plugin(plugin_name)
        try:
            importlib.import_module(f"pyhole.plugins.{plugin_name}")
        except ModuleNotFoundError:
            LOG.debug("No built-in plugin named %s", plugin_name)
        except Exception:
            LOG.exception("Failed to import plugin %s", plugin_name)

    _init_plugins(*args, **kwargs)


def reload_plugins(*args: Any, **kwargs: Any) -> None:
    """Reload all plugins, stopping poll threads first."""
    for instance in _plugin_instances:
        instance.stop()
        # Give poll loops a beat to notice the event.
        time.sleep(0.05)

    Plugin._plugin_classes = []
    _reset_variables()

    plugins_to_reload: list[str] = []
    local_plugin_dir = str(utils.get_home_directory() / "plugins")
    conf = utils.get_config()
    configured = set(conf.get("plugins", type="list", default=["admin"]))

    for mod_name, module in list(sys.modules.items()):
        if module is None:
            continue
        if mod_name.startswith("pyhole.plugins.") and mod_name != "pyhole.plugins":
            short = mod_name.rsplit(".", 1)[-1]
            if short in configured:
                plugins_to_reload.append(mod_name)
            continue
        filename = getattr(module, "__file__", None) or ""
        if local_plugin_dir and local_plugin_dir in filename:
            plugins_to_reload.append(mod_name)

    for plugin_name in plugins_to_reload:
        try:
            importlib.reload(sys.modules[plugin_name])
        except Exception:
            LOG.exception("Failed to reload %s", plugin_name)

    load_plugins(*args, **kwargs)


def active_plugins() -> str:
    return ", ".join(sorted(cls.__name__ for cls in Plugin._plugin_classes))


def active_plugin_classes() -> list[type[Plugin]]:
    return Plugin._plugin_classes


def run_hook_command(
    session: Any, mod_name: str, func: HookFunc, message: Any, arg: Any, **kwargs: Any
) -> None:
    try:
        if arg:
            session.log.debug("Calling: %s.%s(%r)", mod_name, func.__name__, arg)
        else:
            session.log.debug("Calling: %s.%s(None)", mod_name, func.__name__)
        func(message, arg, **kwargs)
    except Exception:
        session.log.exception("Hook %s.%s failed", mod_name, func.__name__)


def run_hook_polls(session: Any) -> None:
    """Polls are started as background threads during plugin init."""
    polls = hook_get_polls()
    if polls:
        session.log.info("Started %d poll hook(s)", len(polls))


def run_msg_regexp_hooks(session: Any, message: Any, private: bool) -> None:
    msg = message.message
    for mod_name, func, msg_regex in hook_get_msg_regexes():
        match = re.search(msg_regex, msg, re.I)
        if match:
            run_hook_command(session, mod_name, func, message, match, private=private)


def run_keyword_hooks(session: Any, message: Any, private: bool) -> None:
    words = message.message.split(" ")
    for mod_name, func, kwarg in hook_get_keywords():
        pattern = rf"^{re.escape(str(kwarg))}(.+)"
        for word in words:
            match = re.search(pattern, word, re.I)
            if match:
                run_hook_command(session, mod_name, func, message, match.group(1), private=private)


def run_command_hooks(session: Any, message: Any, private: bool) -> None:
    msg = message.message
    for mod_name, func, cmd in hook_get_commands():
        session.addressed = False
        cmd_pattern = rf"^{re.escape(str(cmd))}(?:\s+(.*))?$"

        if private:
            match = re.search(cmd_pattern, msg, re.I)
            if match:
                run_hook_command(
                    session,
                    mod_name,
                    func,
                    message,
                    match.group(1),
                    private=private,
                    addressed=session.addressed,
                )

        if msg.startswith(session.command_prefix):
            msg_rest = msg[len(session.command_prefix) :]
        else:
            nick_prefix = session.nick.upper() + ":"
            if msg[: len(session.nick) + 1].upper() == nick_prefix:
                msg_rest = re.sub(r"^\s+", "", msg[len(session.nick) + 1 :])
                session.addressed = True
            else:
                continue

        match = re.search(cmd_pattern, msg_rest, re.I)
        if match:
            run_hook_command(
                session,
                mod_name,
                func,
                message,
                match.group(1),
                private=private,
                addressed=session.addressed,
            )


def poll_messages(session: Any, message: Any, private: bool = False) -> None:
    """Dispatch a received message through command, keyword, and regex hooks."""
    session.addressed = False
    run_command_hooks(session, message, private)
    run_keyword_hooks(session, message, private)
    run_msg_regexp_hooks(session, message, private)
