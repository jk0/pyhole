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

import inspect
import random
import re
import time

import irclib
import plugins


class IRC(irclib.SimpleIRCClient):
    """An IRC connection"""

    def __init__(self, config, network, logger, version):
        irclib.SimpleIRCClient.__init__(self)

        self.log = logger
        self.version = version

        self.admin = config.get("admin")
        self.command_prefix = config.get("command_prefix")
        self.reconnect_delay = config.get("reconnect_delay", "int")
        self.rejoin_delay = config.get("rejoin_delay", "int")

        self.server = network.get("server")
        self.password = network.get("password")
        self.port = network.get("port", "int")
        self.ssl = network.get("ssl", "bool")
        self.nick = network.get("nick")
        self.channels = network.get("channels", "list")

        self.addressed = False

        self.load_plugins()

        self.log.info("Connecting to %s:%d as %s" % (
            self.server,
            self.port,
            self.nick))
        self.connect(
            self.server,
            self.port,
            self.nick,
            self.password,
            ssl=self.ssl)

    def load_plugins(self, reload_plugins=False):
        """Load plugins and their commands respectively"""
        self.plugins = []
        self.commands = []
        self.keywords = []

        if reload_plugins:
            reload(plugins)
        for name in dir(plugins):
            if not name.startswith("_"):
                plugin = "global %s\n%s = plugins.%s.%s(self)" % (
                    name, name, name, name.capitalize())
                if reload_plugins:
                    exec("reload(plugins.%s)\n%s" % (name, plugin))
                else:
                    exec(plugin)
                self.plugins.append(name)
                for k, v in inspect.getmembers(eval(name), inspect.ismethod):
                    if k.startswith("keyword_"):
                        self.keywords.append("%s.%s" % (name, k))
                    elif not k.startswith("_"):
                        self.commands.append("%s.%s" % (name, k))
        self.log.info(self.active_plugins())

    def active_plugins(self):
        """List active plugins"""
        return "Loaded Plugins: %s" % ", ".join(self.plugins)

    def active_commands(self):
        """List active commands"""
        return ", ".join(self.commands)

    def active_keywords(self):
        """List active keywords"""
        return ", ".join(self.keywords)

    def match_direct(self, pattern_p, pattern, needle, haystack):
        """Match a direct command in a message"""
        c = needle.split(".", 1)[1]
        m = re.match(pattern_p % (self.command_prefix, c), haystack)
        if m:
            self.addressed = False
            self.dispatch_command(needle, m.group(1))
        elif re.match(pattern % (self.command_prefix, c), haystack):
            self.addressed = False
            self.dispatch_command(needle)

    def match_addressed(self, pattern_p, pattern, needle, haystack):
        """Match an addressed command in a message"""
        c = needle.split(".", 1)[1]
        m = re.match(pattern_p % (self.nick, c), haystack)
        if m:
            self.addressed = True
            self.dispatch_command(needle, m.group(1))
        elif re.match(pattern % (self.nick, c), haystack):
            self.addressed = True
            self.dispatch_command(needle)

    def match_private(self, pattern_p, pattern, needle, haystack):
        """Match a command in a private message"""
        c = needle.split(".", 1)[1]
        m = re.match(pattern_p % c, haystack)
        if m:
            self.addressed = False
            self.dispatch_command(needle, m.group(1))
        elif re.match(pattern % c, haystack):
            self.addressed = False
            self.dispatch_command(needle)

    def match_keyword(self, pattern, needle, haystack):
        """Match a keyword in a message"""
        k = needle.split("_", 1)[1]
        words = haystack.split(" ")

        for word in words:
            m = re.search(pattern % k, word, re.I)
            if m:
                params = re.sub("\W+", "", m.group(1))
                self.dispatch_command(needle, params)

    def dispatch_command(self, command, params=None):
        try:
            if params:
                self.log.debug("Eval: %s(\"%s\")" % (command, params))
                exec("%s(\"%s\")" % (command, params))
            else:
                self.log.debug("Eval: %s()" % command)
                exec("%s()" % command)
        except Exception as e:
            self.log.error(e)

    def poll_messages(self, message, private=False):
        """Watch for known commands"""
        for c in self.commands:
            self.match_direct("^\%s%s (.+)$", "^\%s%s$", c, message)
            self.match_addressed("^%s: %s (.+)$", "^%s: %s$", c, message)
            if private:
                self.match_private("^%s (.+)$", "^%s$", c, message)

        for k in self.keywords:
            self.match_keyword("%s(.+)", k, message)

    def say(self, msg):
        """Send a privmsg"""
        if self.addressed:
            nick = self.source.split("!")[0]
            self.connection.privmsg(self.target, "%s: %s" % (nick, msg))
        else:
            self.connection.privmsg(self.target, msg)

    def op_user(self, params):
        """Op a user"""
        params = params.split(" ", 1)
        self.connection.mode(params[0], "+o %s" % params[1])

    def deop_user(self, params):
        """De-op a user"""
        params = params.split(" ", 1)
        self.connection.mode(params[0], "-o %s" % params[1])

    def set_nick(self, params):
        """Set IRC nick"""
        self.nick = params
        self.connection.nick(params)

    def join_channel(self, params):
        """Join a channel"""
        channel = params.split(" ", 1)
        self.say("Joining %s" % channel[0])
        if irclib.is_channel(channel[0]):
            self.channels.append(channel[0])
            if len(channel) > 1:
                self.connection.join(channel[0], channel[1])
            else:
                self.connection.join(channel[0])

    def part_channel(self, params):
        """Part a channel"""
        self.channels.remove(params)
        self.say("Parting %s" % params)
        self.connection.part(params)

    def on_nicknameinuse(self, connection, event):
        """Ensure the use of unique IRC nick"""
        random_int = random.randint(1, 100)
        self.log.info("IRC nick '%s' is currently in use" % self.nick)
        self.nick = "%s%d" % (self.nick, random_int)
        self.log.info("Setting IRC nick to '%s'" % self.nick)
        connection.nick("%s" % self.nick)

    def on_welcome(self, connection, event):
        """Join channels upon successful connection"""
        for channel in self.channels:
            c = channel.split(" ", 1)
            if irclib.is_channel(c[0]):
                self.log.info("Joining %s" % c[0])
                if len(c) > 1:
                    connection.join(c[0], c[1])
                else:
                    connection.join(c[0])

    def on_disconnect(self, connection, event):
        """Attempt to reconnect after disconnection"""
        self.log.info("Disconnected from %s:%d" % (self.server, self.port))
        self.log.info("Reconnecting in %d seconds" % self.reconnect_delay)
        time.sleep(self.reconnect_delay)
        self.log.info("Connecting to %s:%d as %s" % (
            self.server,
            self.port,
            self.nick))
        self.connect(
            self.server,
            self.port,
            self.nick,
            self.password,
            ssl=self.ssl)

    def on_kick(self, connection, event):
        """Automatically rejoin channel if kicked"""
        self.target = event.target()

        if event.arguments()[1] == self.nick:
            self.log.info("Kicked from %s" % self.target)
            self.log.info("Rejoining %s in %d seconds" % (
                self.target,
                self.rejoin_delay))
            time.sleep(self.rejoin_delay)
            connection.join(self.target)

    def on_invite(self, connection, event):
        """Join a channel upon invitation"""
        self.source = event.source().split("@", 1)[0]
        self.target = irclib.nm_to_n(event.source())

        if self.source == self.admin:
            self.join_channel(event.arguments()[0])

    def on_ctcp(self, connection, event):
        """Respond to CTCP events"""
        self.source = irclib.nm_to_n(event.source())
        ctcp = event.arguments()[0]

        if ctcp == "VERSION":
            self.log.info("Received CTCP VERSION from %s" % self.source)
            connection.ctcp_reply(self.source, "VERSION %s" % self.version)
        elif ctcp == "PING":
            if len(event.arguments()) > 1:
                self.log.info("Received CTCP PING from %s" % self.source)
                connection.ctcp_reply(
                    self.source,
                    "PING %s" % event.arguments()[1])

    def on_action(self, connection, event):
        """Handle IRC actions"""
        self.source = event.source().split("@", 1)[0]
        self.target = event.target()
        nick = irclib.nm_to_n(event.source())
        msg = event.arguments()[0]

        self.log.info("%s * %s %s" % (self.target, nick, msg))

    def on_privmsg(self, connection, event):
        """Handle private messages"""
        self.source = event.source().split("@", 1)[0]
        self.target = irclib.nm_to_n(event.source())
        msg = event.arguments()[0]

        if self.target != self.nick:
            self.log.info("<%s> %s" % (self.target, msg))
            self.poll_messages(msg, private=True)

    def on_pubmsg(self, connection, event):
        """Handle public messages"""
        self.source = event.source().split("@", 1)[0]
        self.target = event.target()
        nick = irclib.nm_to_n(event.source())
        msg = event.arguments()[0]

        self.log.info("%s <%s> %s" % (self.target, nick, msg))
        self.poll_messages(msg)
