""" Event-based IRC Class """


import inspect
import irclib
import pkgutil
import time

import modules


class IRC(irclib.SimpleIRCClient):
    """ An IRC connection """

    def __init__(self, config, logger):
        irclib.SimpleIRCClient.__init__(self)

        self.log = logger
        self.config = config

        self.server = config.get("server")
        self.port = config.get("port", "int")
        self.nick = config.get("nick")
        self.channel = config.get("channel")
        self.command_prefix = config.get("command_prefix")
        self.commands = []
        self.modules = []
        self.load_modules()

        self.log.info("Connecting to %s:%d as %s" % (
            self.server,
            self.port,
            self.nick))
        self.connect(self.server, self.port, self.nick)

    def load_modules(self):
        """ Load modules and their classes respectively """
        for importer, name, ispkg in pkgutil.iter_modules(modules.__path__):
            module = "global %s\n%s = modules.%s.%s(self)" % (
                name, name, name, name.capitalize())
            exec(module)
            self.modules.append(name)
            for k, v in inspect.getmembers(eval(name), inspect.ismethod):
                if not k.startswith("__"):
                    self.commands.append("%s.%s" % (name, k))
        self.log.info("Loaded Modules: %s" % ", ".join(self.modules))

    def poll_messages(self, message):
        """ Watch for known commands """
        for command in self.commands:
            command = command.split(".", 1)
            if message.startswith("%s%s" % (self.command_prefix, command[1])) \
            or message.startswith("%s: %s" % (self.nick, command[1])):
                self.log.debug("Evaluating: %s()" % ".".join(command))
                eval("%s()" % ".".join(command))

    def on_nicknameinuse(self, connection, event):
        """ Ensure the use of unique IRC nick """
        self.log.info("IRC nick '%s' is currently in use" % self.nick)
        connection.nick("_%s_" % self.nick)
        self.log.info("Setting IRC nick to '_%s_'" % self.nick)

    def on_welcome(self, connection, event):
        """ Join channel upon successful connection """
        if irclib.is_channel(self.channel):
            self.log.info("Joining %s" % self.channel)
            connection.join(self.channel)

    def on_disconnect(self, connection, event):
        """ Attempt to reconnect after disconnection """
        self.log.info("Disconnected from %s:%d" % (self.server, self.port))
        time.sleep(15)
        self.log.info("Attempting to reconnect in 15 seconds")
        self.connect(self.server, self.port, self.nick)

    def on_privmsg(self, connection, event):
        """ Handle private messages """
        nick = event.source().split("!")[0]
        msg = event.arguments()[0]

        if nick != self.nick:
            self.log.info("<%s> %s" % (nick, msg))
            self.poll_messages(msg)

    def on_pubmsg(self, connection, event):
        """ Handle public messages """
        target = event.target()
        nick = event.source().split("!")[0]
        msg = event.arguments()[0]

        if target == self.channel:
            self.log.info("%s <%s> %s" % (target, nick, msg))
            self.poll_messages(msg)
