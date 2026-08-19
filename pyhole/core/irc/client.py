# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""IRC client."""

from __future__ import annotations

import functools
import random
import ssl
import time
from typing import Any

import irc.client as irclib
from irc import connection

from pyhole.core import logger, plugin, queue, utils, version
from pyhole.core.irc import message


def _ssl_wrapper(server: str, verify: bool):
    ctx = ssl.create_default_context()
    if not verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return functools.partial(ctx.wrap_socket, server_hostname=server)


class Client(irclib.SimpleIRCClient):
    """An IRC connection."""

    def __init__(self, network: str) -> None:
        super().__init__()

        logger.setup_logger(str(network))

        pyhole_config = utils.get_config()
        network_config = utils.get_config(network)

        self.log = logger.get_logger(str(network))
        self.version = version.version_string()
        self.source: str | None = None
        self.target: str | None = None
        self.addressed = False

        self.admins = pyhole_config.get("admins", type="list")
        self.command_prefix = pyhole_config.get("command_prefix")
        self.reconnect_delay = pyhole_config.get("reconnect_delay", type="int")
        self.rejoin_delay = pyhole_config.get("rejoin_delay", type="int")

        self.server = network_config.get("server")
        self.password = network_config.get("password", default=None)
        self.port = network_config.get("port", type="int", default=6667)
        self.use_ssl = network_config.get("ssl", type="bool", default=False)
        self.ssl_verify = network_config.get("ssl_verify", type="bool", default=True)
        self.ipv6 = network_config.get("ipv6", type="bool", default=False)
        self.bind_to = network_config.get("bind_to", default=None)
        self.nick = network_config.get("nick")
        self.username = network_config.get("username", default=None)
        self.identify_password = network_config.get("identify_password", default=None)
        self.channels = network_config.get("channels", type="list")

        self.load_plugins()
        self.log.info("Connecting to %s:%d as %s", self.server, self.port, self.nick)
        self._connect()

    def _connect_factory(self) -> connection.Factory:
        wrapper = _ssl_wrapper(self.server, self.ssl_verify) if self.use_ssl else None
        kwargs: dict[str, Any] = {"ipv6": self.ipv6}
        if wrapper is not None:
            kwargs["wrapper"] = wrapper
        if self.bind_to:
            kwargs["bind_address"] = (self.bind_to, 0)
        return connection.Factory(**kwargs)

    def _connect(self) -> None:
        self.connect(
            self.server,
            self.port,
            self.nick,
            self.password,
            username=self.username,
            connect_factory=self._connect_factory(),
        )

    def load_plugins(self, reload_plugins: bool = False) -> None:
        if reload_plugins:
            plugin.reload_plugins(session=self)
        else:
            plugin.load_plugins(session=self)
        self.log.info("Loaded Plugins: %s", plugin.active_plugins())
        plugin.run_hook_polls(self)

    def notice(self, target: str, msg: str) -> None:
        self.connection.notice(target, msg)

    def reply(self, target: str, msg: str) -> None:
        self.connection.privmsg(target, msg)

    def op_user(self, params: str) -> None:
        channel, _, nick = params.partition(" ")
        self.connection.mode(channel, f"+o {nick}")

    def deop_user(self, params: str) -> None:
        channel, _, nick = params.partition(" ")
        self.connection.mode(channel, f"-o {nick}")

    def set_nick(self, params: str) -> None:
        self.nick = params
        self.connection.nick(params)

    def join_channel(self, params: str) -> None:
        parts = params.split(" ", 1)
        self.log.info("Joining %s", parts[0])
        if irclib.is_channel(parts[0]):
            self.channels.append(parts[0])
            if len(parts) > 1:
                self.connection.join(parts[0], parts[1])
            else:
                self.connection.join(parts[0])

    def part_channel(self, params: str) -> None:
        if params in self.channels:
            self.channels.remove(params)
        self.log.info("Parting %s", params)
        self.connection.part(params)

    def on_nicknameinuse(self, connection: Any, _event: Any) -> None:
        random_int = random.randint(1, 100)
        self.log.info("IRC nick '%s' is currently in use", self.nick)
        self.nick = f"{self.nick}{random_int}"
        self.log.info("Setting IRC nick to '%s'", self.nick)
        connection.nick(self.nick)
        time.sleep(1)

    def on_welcome(self, connection: Any, _event: Any) -> None:
        if self.identify_password:
            self.reply("NickServ", f"IDENTIFY {self.identify_password}")

        for channel in self.channels:
            parts = channel.split(" ", 1)
            if not irclib.is_channel(parts[0]):
                continue
            if len(parts) > 1:
                connection.join(parts[0], parts[1])
            else:
                connection.join(parts[0])

        queue.MessageQueue().watch(self)

    def on_disconnect(self, _connection: Any, _event: Any) -> None:
        self.log.info("Disconnected from %s:%d.", self.server, self.port)
        self.log.info("Reconnecting in %d seconds.", self.reconnect_delay)
        time.sleep(self.reconnect_delay)
        self.log.info("Connecting to %s:%d as %s.", self.server, self.port, self.nick)
        self._connect()

    def on_kick(self, connection: Any, event: Any) -> None:
        source = event.source.nick
        target = event.target
        nick, reason = event.arguments[0], event.arguments[1] if len(event.arguments) > 1 else ""

        if nick == self.nick:
            self.log.info("-%s- kicked by %s: %s", target, source, reason)
            self.log.info("-%s- rejoining in %d seconds", target, self.rejoin_delay)
            time.sleep(self.rejoin_delay)
            connection.join(target)
        else:
            self.log.info("-%s- %s was kicked by %s: %s", target, nick, source, reason)

    def on_invite(self, _connection: Any, event: Any) -> None:
        source = str(event.source).split("@", 1)[0]
        if source in self.admins:
            self.join_channel(event.arguments[0])

    def on_ctcp(self, connection: Any, event: Any) -> None:
        source = event.source.nick
        ctcp = event.arguments[0]
        if ctcp == "VERSION":
            self.log.info("Received CTCP VERSION from %s", source)
            connection.ctcp_reply(source, f"VERSION {self.version}")
        elif ctcp == "PING" and len(event.arguments) > 1:
            self.log.info("Received CTCP PING from %s", source)
            connection.ctcp_reply(source, f"PING {event.arguments[1]}")

    def on_join(self, _connection: Any, event: Any) -> None:
        self.log.info("-%s- %s joined", event.target, event.source.nick)

    def on_part(self, _connection: Any, event: Any) -> None:
        self.log.info("-%s- %s left", event.target, event.source.nick)

    def on_quit(self, _connection: Any, event: Any) -> None:
        self.log.info("%s quit", event.source.nick)

    def on_action(self, _connection: Any, event: Any) -> None:
        self.log.info("-%s- * %s %s", event.target, event.source.nick, event.arguments[0])

    def on_privnotice(self, _connection: Any, event: Any) -> None:
        source = event.source.nick if event.source is not None else None
        self.log.info("-%s- %s", source, event.arguments[0])

    def on_pubnotice(self, _connection: Any, event: Any) -> None:
        source = event.source.nick if event.source is not None else None
        self.log.info("-%s- <%s> %s", event.target, source, event.arguments[0])

    def on_privmsg(self, _connection: Any, event: Any) -> None:
        msg = event.arguments[0]
        source = str(event.source).split("@", 1)[0]
        target = event.source.nick
        wrapped = message.Reply(self, msg, source, target)
        self.log.info("<%s> %s", target, msg)
        plugin.poll_messages(self, wrapped, private=True)

    def on_pubmsg(self, _connection: Any, event: Any) -> None:
        nick = event.source.nick
        msg = event.arguments[0]
        source = str(event.source).split("@", 1)[0]
        target = event.target
        self.log.info("-%s- <%s> %s", target, nick, msg)
        wrapped = message.Reply(self, msg, source, target)
        plugin.poll_messages(self, wrapped)
