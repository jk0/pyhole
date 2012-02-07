#   Copyright 2010-2011 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Event-based IRC Class"""

import multiprocessing
import random
import re
import sys
import time
import urllib

import irclib
import log
import plugin
import utils
import version


LOG = log.get_logger()
CONFIG = utils.get_config()


class IRC(irclib.SimpleIRCClient):
    """An IRClib connection."""

    def __init__(self, network):
        irclib.SimpleIRCClient.__init__(self)
        network_config = utils.get_config(network)

        self.log = log.get_logger(str(network))
        self.version = version.version_string()
        self.source = None
        self.target = None
        self.addressed = False

        self.admins = CONFIG.get("admins", type="list")
        self.command_prefix = CONFIG.get("command_prefix")
        self.reconnect_delay = CONFIG.get("reconnect_delay", type="int")
        self.rejoin_delay = CONFIG.get("rejoin_delay", type="int")

        self.server = network_config.get("server")
        self.password = network_config.get("password", default="")
        self.port = network_config.get("port", type="int", default=6667)
        self.ssl = network_config.get("ssl", type="bool", default=False)
        self.ipv6 = network_config.get("ipv6", type="bool", default=False)
        self.bind_to = network_config.get("bind_to", default="")
        self.nick = network_config.get("nick")
        self.identify_password = network_config.get("identify_password",
                default="")
        self.channels = network_config.get("channels", type="list")

        self.load_plugins()

        self.log.info("Connecting to %s:%d as %s" % (self.server, self.port,
                self.nick))
        self.connect(self.server, self.port, self.nick, self.password,
                ssl=self.ssl, ipv6=self.ipv6, localaddress=self.bind_to)

    def load_plugins(self, reload_plugins=False):
        """Load plugins and their commands respectively."""
        if reload_plugins:
            plugin.reload_plugins(irc=self)
        else:
            plugin.load_plugins(irc=self)

        self.log.info("Loaded Plugins: %s" % active_plugins())

    def run_hook_command(self, mod_name, func, arg, **kwargs):
        """Make a call to a plugin hook."""
        try:
            func(arg, **kwargs)
            if arg:
                self.log.debug("Calling: %s.%s(\"%s\")" % (mod_name,
                        func.__name__, arg))
            else:
                self.log.debug("Calling: %s.%s(None)" % (mod_name,
                        func.__name__))
        except Exception, exc:
            self.log.error(exc)

    def run_msg_regexp_hooks(self, message, private):
        """Run regexp hooks."""
        for mod_name, func, msg_regex in plugin.hook_get_msg_regexs():
            match = re.search(msg_regex, message, re.I)
            if match:
                self.run_hook_command(mod_name, func, match, private=private,
                        full_message=message)

    def run_keyword_hooks(self, message, private):
        """Run keyword hooks."""
        words = message.split(" ")
        for mod_name, func, kwarg in plugin.hook_get_keywords():
            for word in words:
                match = re.search("^%s(.+)" % kwarg, word, re.I)
                if match:
                    self.run_hook_command(mod_name, func, match.group(1),
                            private=private, full_message=message)

    def run_command_hooks(self, message, private):
        """Run command hooks."""
        for mod_name, func, cmd in plugin.hook_get_commands():
            self.addressed = False

            if private:
                match = re.search("^%s$|^%s\s(.*)$" % (cmd, cmd), message,
                        re.I)
                if match:
                    self.run_hook_command(mod_name, func, match.group(1),
                            private=private, addressed=self.addressed,
                            full_message=message)

            if message.startswith(self.command_prefix):
                # Strip off command prefix
                msg_rest = message[len(self.command_prefix):]
            else:
                # Check for command starting with nick being addressed
                msg_start_upper = message[:len(self.nick) + 1].upper()
                if msg_start_upper == self.nick.upper() + ":":
                    # Get rest of string after "nick:" and white spaces
                    msg_rest = re.sub("^\s+", "",
                            message[len(self.nick) + 1:])
                else:
                    continue

                self.addressed = True

            match = re.search("^%s$|^%s\s(.*)$" % (cmd, cmd), msg_rest, re.I)
            if match:
                self.run_hook_command(mod_name, func, match.group(1),
                        private=private, addressed=self.addressed,
                        full_message=message)

    def poll_messages(self, message, private=False):
        """Watch for known commands."""
        self.addressed = False

        self.run_command_hooks(message, private)
        self.run_keyword_hooks(message, private)
        self.run_msg_regexp_hooks(message, private)

    def reply(self, msg):
        """Send a privmsg."""
        if not hasattr(msg, "encode"):
            try:
                msg = str(msg)
            except Exception:
                self.log.error("msg cannot be converted to string")
                return

        msg = msg.encode("utf-8").split("\n")
        # 10 is completely arbitrary for now
        if len(msg) > 10:
            msg = msg[0:8]
            msg.append("...")

        for line in msg:
            if self.addressed:
                source = self.source.split("!")[0]
                self.connection.privmsg(self.target, "%s: %s" % (source, line))
                self.log.info("-%s- <%s> %s: %s" % (self.target, self.nick,
                        source, line))
            else:
                self.connection.privmsg(self.target, line)
                if irclib.is_channel(self.target):
                    self.log.info("-%s- <%s> %s" % (self.target, self.nick,
                            line))
                else:
                    self.log.info("<%s> %s" % (self.nick, line))

    def privmsg(self, target, msg):
        """Send a privmsg."""
        self.connection.privmsg(target, msg)

    def op_user(self, params):
        """Op a user."""
        params = params.split(" ", 1)
        self.connection.mode(params[0], "+o %s" % params[1])

    def deop_user(self, params):
        """De-op a user."""
        params = params.split(" ", 1)
        self.connection.mode(params[0], "-o %s" % params[1])

    def set_nick(self, params):
        """Set IRC nick."""
        self.nick = params
        self.connection.nick(params)

    def join_channel(self, params):
        """Join a channel."""
        channel = params.split(" ", 1)
        self.reply("Joining %s" % channel[0])
        if irclib.is_channel(channel[0]):
            self.channels.append(channel[0])
            if len(channel) > 1:
                self.connection.join(channel[0], channel[1])
            else:
                self.connection.join(channel[0])

    def part_channel(self, params):
        """Part a channel."""
        self.channels.remove(params)
        self.reply("Parting %s" % params)
        self.connection.part(params)

    def fetch_url(self, url, name):
        """Fetch a URL."""
        class PyholeURLopener(urllib.FancyURLopener):
            """Set a custom user agent."""
            version = self.version

        urllib._urlopener = PyholeURLopener()

        try:
            return urllib.urlopen(url)
        except IOError:
            self.reply("Unable to fetch %s data" % name)
            return None

    def on_nicknameinuse(self, connection, _event):
        """Ensure the use of unique IRC nick."""
        random_int = random.randint(1, 100)
        self.log.info("IRC nick '%s' is currently in use" % self.nick)
        self.nick = "%s%d" % (self.nick, random_int)
        self.log.info("Setting IRC nick to '%s'" % self.nick)
        connection.nick("%s" % self.nick)
        # Try to prevent nick flooding
        time.sleep(1)

    def on_welcome(self, connection, _event):
        """Join channels upon successful connection."""
        if self.identify_password:
            self.privmsg("NickServ", "IDENTIFY %s" % self.identify_password)

        for channel in self.channels:
            channel = channel.split(" ", 1)
            if irclib.is_channel(channel[0]):
                if len(channel) > 1:
                    connection.join(channel[0], channel[1])
                else:
                    connection.join(channel[0])

    def on_disconnect(self, _connection, _event):
        """Attempt to reconnect after disconnection."""
        self.log.info("Disconnected from %s:%d" % (self.server, self.port))
        self.log.info("Reconnecting in %d seconds" % self.reconnect_delay)
        time.sleep(self.reconnect_delay)
        self.log.info("Connecting to %s:%d as %s" % (self.server, self.port,
                self.nick))
        self.connect(self.server, self.port, self.nick, self.password,
                ssl=self.ssl)

    def on_kick(self, connection, event):
        """Automatically rejoin channel if kicked."""
        source = irclib.nm_to_n(event.source())
        target = event.target()
        nick, reason = event.arguments()

        if nick == self.nick:
            self.log.info("-%s- kicked by %s: %s" % (target, source, reason))
            self.log.info("-%s- rejoining in %d seconds" % (target,
                    self.rejoin_delay))
            time.sleep(self.rejoin_delay)
            connection.join(target)
        else:
            self.log.info("-%s- %s was kicked by %s: %s" % (target, nick,
                    source, reason))

    def on_invite(self, _connection, event):
        """Join a channel upon invitation."""
        source = event.source().split("@", 1)[0]
        if source in self.admins:
            self.join_channel(event.arguments()[0])

    def on_ctcp(self, connection, event):
        """Respond to CTCP events."""
        source = irclib.nm_to_n(event.source())
        ctcp = event.arguments()[0]

        if ctcp == "VERSION":
            self.log.info("Received CTCP VERSION from %s" % source)
            connection.ctcp_reply(source, "VERSION %s" % self.version)
        elif ctcp == "PING":
            if len(event.arguments()) > 1:
                self.log.info("Received CTCP PING from %s" % source)
                connection.ctcp_reply(source,
                        "PING %s" % event.arguments()[1])

    def on_join(self, _connection, event):
        """Handle joins."""
        target = event.target()
        source = irclib.nm_to_n(event.source())
        self.log.info("-%s- %s joined" % (target, source))

    def on_part(self, _connection, event):
        """Handle parts."""
        target = event.target()
        source = irclib.nm_to_n(event.source())
        self.log.info("-%s- %s left" % (target, source))

    def on_quit(self, _connection, event):
        """Handle quits."""
        source = irclib.nm_to_n(event.source())
        self.log.info("%s quit" % source)

    def on_action(self, _connection, event):
        """Handle IRC actions."""
        target = event.target()
        source = irclib.nm_to_n(event.source())
        msg = event.arguments()[0]
        self.log.info(unicode("-%s- * %s %s" % (target, source, msg), "utf-8"))

    def on_privnotice(self, _connection, event):
        """Handle private notices."""
        if event.source() is not None:
            source = irclib.nm_to_n(event.source())
        else:
            source = None
        msg = event.arguments()[0]
        self.log.info(unicode("-%s- %s" % (source, msg), "utf-8"))

    def on_pubnotice(self, _connection, event):
        """Handle public notices."""
        target = event.target()
        if event.source() is not None:
            source = irclib.nm_to_n(event.source())
        else:
            source = None
        msg = event.arguments()[0]
        self.log.info(unicode("-%s- <%s> %s" % (target, source, msg),
                "utf-8"))

    def on_privmsg(self, _connection, event):
        """Handle private messages."""
        self.source = event.source().split("@", 1)[0]
        self.target = irclib.nm_to_n(event.source())
        msg = event.arguments()[0]

        if self.target != self.nick:
            self.log.info(unicode("<%s> %s" % (self.target, msg), "utf-8"))
            self.poll_messages(msg, private=True)

    def on_pubmsg(self, _connection, event):
        """Handle public messages."""
        self.source = event.source().split("@", 1)[0]
        self.target = event.target()
        nick = irclib.nm_to_n(event.source())
        msg = event.arguments()[0]

        self.log.info(unicode("-%s- <%s> %s" % (self.target, nick, msg),
                "utf-8"))
        self.poll_messages(msg)


class IRCProcess(multiprocessing.Process):
    """An IRC network connection process."""
    def __init__(self, irc_network):
        super(IRCProcess, self).__init__()
        self.irc_network = irc_network
        self.reconnect_delay = CONFIG.get("reconnect_delay", type="int")

    def run(self):
        """An IRC network connection."""
        while True:
            try:
                connection = IRC(self.irc_network)
            except Exception, exc:
                LOG.error(exc)
                LOG.error("Retrying in %d seconds" % self.reconnect_delay)
                time.sleep(self.reconnect_delay)
                continue

            try:
                connection.start()
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception, exc:
                LOG.error(exc)
                LOG.error("Retrying in %d seconds" % self.reconnect_delay)
                time.sleep(self.reconnect_delay)
                continue


def active_plugins():
    """List active plugins."""
    return ", ".join(sorted(plugin.active_plugins()))


def active_commands():
    """List active commands."""
    return ", ".join(sorted(plugin.active_commands()))


def active_keywords():
    """List active keywords."""
    return ", ".join(sorted(plugin.active_keywords()))


def main():
    """Main IRC loop."""
    networks = CONFIG.get("networks", type="list")

    LOG.info("Starting %s" % version.version_string())
    LOG.info("Connecting to IRC Networks: %s" % ", ".join(networks))
    for network in networks:
        proc = IRCProcess(network)
        proc.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        LOG.info("Caught KeyboardInterrupt, shutting down")
