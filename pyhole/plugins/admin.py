# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole administration plugin."""

from __future__ import annotations

from pyhole.core import plugin, utils


class Admin(plugin.Plugin):
    """Administer your bot."""

    @plugin.hook_add_command("help")
    def help(self, message, params=None, **kwargs):
        """Learn how to use plugins (ex: .help <command>)."""
        if params:
            doc = _find_doc_string(params)
            message.dispatch(doc if doc else f"No help available: {params}")
            return

        message.dispatch(self.help.__doc__)
        commands = plugin.active_commands()
        keywords = plugin.active_keywords()
        patterns = plugin.active_msg_regexes()
        pollers = plugin.active_polls()
        if commands:
            message.dispatch(f"Active Commands: {commands}")
        if keywords:
            message.dispatch(f"Active Keywords: {keywords}")
        if patterns:
            message.dispatch(f"Active Patterns: {patterns}")
        if pollers:
            message.dispatch(f"Active Pollers: {pollers}")

    @plugin.hook_add_command("version")
    def version(self, message, params=None, **kwargs):
        """Display the current version."""
        message.dispatch(self.session.version)

    @plugin.hook_add_command("reload")
    @utils.admin
    def reload(self, message, params=None, **kwargs):
        """Reload all plugins."""
        self.session.load_plugins(reload_plugins=True)
        message.dispatch(f"Loaded Plugins: {plugin.active_plugins()}")

    @plugin.hook_add_command("op")
    @utils.admin
    @utils.require_params
    def op(self, message, params=None, **kwargs):
        """Op a user (ex: .op <channel> <nick>)."""
        self.session.op_user(params)

    @plugin.hook_add_command("deop")
    @utils.admin
    @utils.require_params
    def deop(self, message, params=None, **kwargs):
        """De-op a user (ex: .deop <channel> <nick>)."""
        self.session.deop_user(params)

    @plugin.hook_add_command("nick")
    @utils.admin
    @utils.require_params
    def nick(self, message, params=None, **kwargs):
        """Change nick (ex: .nick <nick>)."""
        self.session.set_nick(params)

    @plugin.hook_add_command("join")
    @utils.admin
    @utils.require_params
    def join(self, message, params=None, **kwargs):
        """Join a channel (ex: .join #channel [<key>])."""
        self.session.join_channel(params)

    @plugin.hook_add_command("part")
    @utils.admin
    @utils.require_params
    def part(self, message, params=None, **kwargs):
        """Part a channel (ex: .part <channel>)."""
        self.session.part_channel(params)

    @plugin.hook_add_command("say")
    @utils.admin
    @utils.require_params
    def say(self, message, params=None, **kwargs):
        """Send a reply (ex: .say <channel>|<nick> message)."""
        target, _, msg = params.partition(" ")
        if not msg:
            message.dispatch(self.say.__doc__)
            return
        self.session.reply(target, msg)


def _find_doc_string(params: str) -> str | None:
    for plugin_cls in plugin.active_plugin_classes():
        if plugin_cls.__name__.upper() == params.upper():
            return plugin_cls.__doc__
    for _, cmd_hook, cmd in plugin.hook_get_commands():
        if str(cmd).upper() == params.upper():
            return cmd_hook.__doc__
    for _, kw_hook, kw in plugin.hook_get_keywords():
        if str(kw).upper() == params.upper():
            return kw_hook.__doc__
    return None
