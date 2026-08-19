# Copyright 2015-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Slack client (Socket Mode)."""

from __future__ import annotations

import time
from typing import Any

from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient

from pyhole.core import logger, plugin, queue, utils, version
from pyhole.core.slack import message


class Client:
    """A Slack Socket Mode connection."""

    def __init__(self, network: str) -> None:
        logger.setup_logger(str(network))

        pyhole_config = utils.get_config()
        network_config = utils.get_config(network)

        self.addressed = False
        self.web: WebClient | None = None
        self.socket: SocketModeClient | None = None
        self._users: dict[str, str] = {}
        self._channels: dict[str, str] = {}
        self.bot_user_id: str | None = None

        self.log = logger.get_logger(str(network))
        self.version = version.version_string()

        self.admins = pyhole_config.get("admins", type="list")
        self.command_prefix = pyhole_config.get("command_prefix")

        self.api_token = network_config.get("api_token")
        self.app_token = network_config.get("app_token", default="")
        self.nick = network_config.get("nick")

        if not self.app_token:
            raise RuntimeError(
                f"Slack network [{network}] needs app_token (xapp-...) for Socket Mode"
            )

        self.load_plugins()

    def load_plugins(self, reload_plugins: bool = False) -> None:
        if reload_plugins:
            plugin.reload_plugins(session=self)
        else:
            plugin.load_plugins(session=self)
        self.log.info("Loaded Plugins: %s", plugin.active_plugins())
        plugin.run_hook_polls(self)

    def start(self) -> None:
        self.web = WebClient(token=self.api_token)
        auth = self.web.auth_test()
        self.bot_user_id = auth.get("user_id")
        if auth.get("user"):
            self.nick = auth["user"]

        self.socket = SocketModeClient(app_token=self.app_token, web_client=self.web)
        self.socket.socket_mode_request_listeners.append(self._on_request)

        queue.MessageQueue().watch(self)
        self.log.info("Connecting to Slack as %s", self.nick)
        self.socket.connect()
        while True:
            time.sleep(1)

    def _on_request(self, client: SocketModeClient, req: SocketModeRequest) -> None:
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
        if req.type != "events_api":
            return
        event = req.payload.get("event") or {}
        if event.get("type") != "message" or event.get("subtype"):
            return
        if event.get("user") == self.bot_user_id:
            return
        if event.get("bot_id") and not event.get("user"):
            return

        channel_id = event.get("channel", "")
        user_id = event.get("user", "")
        text = event.get("text") or ""
        channel = self._channel_name(channel_id)
        user = self._user_name(user_id)
        self.log.info("-#%s- <%s> %s", channel, user, text)
        wrapped = message.Reply(self, text, user, channel)
        plugin.poll_messages(self, wrapped)

    def _channel_name(self, channel_id: str) -> str:
        if channel_id in self._channels:
            return self._channels[channel_id]
        name = channel_id
        try:
            info = self.web.conversations_info(channel=channel_id)  # type: ignore[union-attr]
            name = info["channel"].get("name") or channel_id
        except Exception:
            self.log.debug("Could not resolve channel %s", channel_id, exc_info=True)
        self._channels[channel_id] = name
        return name

    def _user_name(self, user_id: str) -> str:
        if user_id in self._users:
            return self._users[user_id]
        name = user_id
        try:
            info = self.web.users_info(user=user_id)  # type: ignore[union-attr]
            name = info["user"].get("name") or user_id
        except Exception:
            self.log.debug("Could not resolve user %s", user_id, exc_info=True)
        self._users[user_id] = name
        return name

    def reply(self, target: str, msg: str) -> None:
        if self.web is None:
            self.log.error("Slack client is not connected")
            return
        channel_id = self._resolve_target(target)
        try:
            self.web.chat_postMessage(channel=channel_id, text=msg)
        except Exception:
            self.log.exception("Unable to send Slack message to %s", target)

    def notice(self, target: str, msg: str) -> None:
        self.reply(target, msg)

    def _resolve_target(self, target: str) -> str:
        for channel_id, name in self._channels.items():
            if name == target or channel_id == target:
                return channel_id
        for user_id, name in self._users.items():
            if name == target or user_id == target:
                return user_id
        return target

    def op_user(self, *args: Any, **kwargs: Any) -> None:
        return None

    def deop_user(self, *args: Any, **kwargs: Any) -> None:
        return None

    def set_nick(self, *args: Any, **kwargs: Any) -> None:
        return None

    def join_channel(self, *args: Any, **kwargs: Any) -> None:
        return None

    def part_channel(self, *args: Any, **kwargs: Any) -> None:
        return None
