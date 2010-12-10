"""Event-based IRC Class"""


import inspect
import random
import re
import time

import irclib
import modules


class IRC(irclib.SimpleIRCClient):
    """An IRC connection"""

    def __init__(self, config, logger):
        irclib.SimpleIRCClient.__init__(self)

        self.log = logger
        self.config = config

        self.admin = config.get("admin")
        self.server = config.get("server")
        self.port = config.get("port", "int")
        self.ssl = config.get("ssl", "bool")
        self.nick = config.get("nick")
        self.channels = config.get("channels", "list")
        self.command_prefix = config.get("command_prefix")
        self.reconnect_delay = config.get("reconnect_delay", "int")
        self.rejoin_delay = config.get("rejoin_delay", "int")
        self.load_modules()

        self.log.info("Connecting to %s:%d as %s" % (
            self.server,
            self.port,
            self.nick))
        self.connect(self.server, self.port, self.nick, ssl=self.ssl)

    def load_modules(self, reload_mods=False):
        """Load modules and their classes respectively"""
        self.modules = []
        self.commands = []

        if reload_mods:
            reload(modules)
        for name in dir(modules):
            if not name.startswith("__"):
                module = "global %s\n%s = modules.%s.%s(self)" % (
                    name, name, name, name.capitalize())
                if reload_mods:
                    exec("reload(modules.%s)\n%s" % (name, module))
                else:
                    exec(module)
                self.modules.append(name)
                for k, v in inspect.getmembers(eval(name), inspect.ismethod):
                    if not k.startswith("__"):
                        self.commands.append("%s.%s" % (name, k))
        self.log.info(self.active_modules())

    def active_modules(self):
        """List active modules"""
        return "Loaded Modules: %s" % ", ".join(self.modules)

    def active_commands(self):
        """List active commands"""
        return ", ".join(self.commands)

    def active_channels(self):
        """List active channels"""
        return "Active Channels: %s" % ", ".join(self.channels)

    def match_direct(self, pattern_p, pattern, needle, haystack):
        """Match a direct command in a message"""
        c = needle.split(".", 1)
        m = re.match(pattern_p % (self.command_prefix, c[1]), haystack)
        if m:
            self.log.debug("Eval: %s(\"%s\")" % (".".join(c), m.group(1)))
            eval("%s(\"%s\")" % (".".join(c), m.group(1)))
        elif re.match(pattern % (self.command_prefix, c[1]), haystack):
            self.log.debug("Eval: %s()" % ".".join(c))
            eval("%s()" % ".".join(c))

    def match_addressed(self, pattern_p, pattern, needle, haystack):
        """Match an addressed command in a message"""
        c = needle.split(".", 1)
        m = re.match(pattern_p % (self.nick, c[1]), haystack)
        if m:
            self.log.debug("Eval: %s(\"%s\")" % (".".join(c), m.group(1)))
            eval("%s(\"%s\")" % (".".join(c), m.group(1)))
        elif re.match(pattern % (self.nick, c[1]), haystack):
            self.log.debug("Eval: %s()" % ".".join(c))
            eval("%s()" % ".".join(c))

    def match_private(self, pattern_p, pattern, needle, haystack):
        """Match a command in a private message"""
        c = needle.split(".", 1)
        m = re.match(pattern_p % c[1], haystack)
        if m:
            self.log.debug("Eval: %s(\"%s\")" % (".".join(c), m.group(1)))
            eval("%s(\"%s\")" % (".".join(c), m.group(1)))
        elif re.match(pattern % c[1], haystack):
            self.log.debug("Eval: %s()" % ".".join(c))
            eval("%s()" % ".".join(c))

    def poll_messages(self, message, private=False):
        """Watch for known commands"""
        for command in self.commands:
            self.match_direct("^%s%s (.+)$", "^%s%s$", command, message)
            self.match_addressed("^%s: %s (.+)$", "^%s: %s$", command, message)
            if private:
                self.match_private("^%s (.+)$", "^%s$", command, message)

    def send_msg(self, msg):
        """Send a privmsg"""
        self.connection.privmsg(self.target, msg)

    def op_user(self, params):
        """Op a user"""
        params = params.split(" ", 1)
        self.connection.mode(params[0], "+o %s" % params[1])

    def set_nick(self, params):
        """Set IRC nick"""
        self.nick = params
        self.connection.nick(params)

    def join_channel(self, params):
        """Join a channel"""
        channel = params.split(" ", 1)
        self.send_msg("Joining %s" % channel[0])
        if irclib.is_channel(channel[0]):
            self.channels.append(channel[0])
            if len(channel) > 1:
                self.connection.join(channel[0], channel[1])
            else:
                self.connection.join(channel[0])

    def part_channel(self, params):
        """Part a channel"""
        self.channels.remove(params)
        self.send_msg("Parting %s" % params)
        self.connection.part(params)

    def on_nicknameinuse(self, connection, event):
        """Ensure the use of unique IRC nick"""
        random_int = random.randint(1, 100)
        self.log.info("IRC nick '%s' is currently in use" % self.nick)
        self.nick = "%s%d" % (self.nick, random_int)
        self.log.info("Setting IRC nick to '%s'" % self.nick)
        connection.nick("%s" % self.nick)

    def on_welcome(self, connection, event):
        """Join channel upon successful connection"""
        for channel in self.channels:
            if irclib.is_channel(channel):
                self.log.info("Joining %s" % channel)
                connection.join(channel)

    def on_disconnect(self, connection, event):
        """Attempt to reconnect after disconnection"""
        self.log.info("Disconnected from %s:%d" % (self.server, self.port))
        time.sleep(self.reconnect_delay)
        self.log.info("Reconnecting in %d seconds" % self.reconnect_delay)
        self.connect(self.server, self.port, self.nick)

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

    def on_privmsg(self, connection, event):
        """Handle private messages"""
        self.source = event.source().split("@", 1)[0]
        self.target = event.source().split("!", 1)[0]
        msg = event.arguments()[0]

        if self.target != self.nick:
            self.log.info("<%s> %s" % (self.target, msg))
            try:
                self.poll_messages(msg, private=True)
            except Exception as e:
                self.log.error(e)

    def on_pubmsg(self, connection, event):
        """Handle public messages"""
        self.source = event.source().split("@", 1)[0]
        self.target = event.target()
        nick = event.source().split("!", 1)[0]
        msg = event.arguments()[0]

        self.log.info("%s <%s> %s" % (self.target, nick, msg))
        try:
            self.poll_messages(msg)
        except Exception as e:
            self.log.error(e)
