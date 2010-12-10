"""Pyhole Administration"""


import sys

from pyhole import utils


class Admin(object):
    """Provide administration functionality"""

    def __init__(self, irc):
        self.irc = irc

    def help(self, params=None):
        """Learn how to use active modules (ex: .help <module.command>)"""
        if params:
            # Temporarily load the class for __doc__ access
            try:
                module = params.split(".")[0]
                exec("import %s\n%s = %s.%s(self.irc)" % (
                    module,
                    module.capitalize(),
                    module,
                    module.capitalize()))

                doc = eval("%s.__doc__" % params.capitalize())
                self.irc.say(doc)

                # Destroy the class
                exec("%s = None" % module.capitalize())
            except ImportError as e:
                self.irc.log.error(e)
        else:
            self.irc.say(self.help.__doc__)
            self.irc.say(self.irc.active_commands())

    @utils.admin
    def reload(self, params=None):
        """Reload all modules"""
        self.irc.load_modules(reload_mods=True)
        self.irc.say(self.irc.active_modules())

    @utils.admin
    def info(self, params=None):
        """Access various statistics (ex: .info <topic>)"""
        if params == "channels":
            self.irc.say(self.irc.active_channels())
        else:
            self.irc.say(self.info.__doc__)

    @utils.admin
    def op(self, params=None):
        """Op a user (ex: .op <channel> <nick>)"""
        if params:
            self.irc.op_user(params)
        else:
            self.irc.say(self.op.__doc__)

    @utils.admin
    def nick(self, params=None):
        """Change IRC nick (ex: .nick <nick>)"""
        if params:
            self.irc.set_nick(params)
        else:
            self.irc.say(self.nick.__doc__)

    @utils.admin
    def join(self, params=None):
        """Join a channel (ex: .join #channel [<key>])"""
        if params:
            self.irc.join_channel(params)
        else:
            self.irc.say(self.join.__doc__)

    @utils.admin
    def part(self, params=None):
        """Part a channel (ex: .part <channel>)"""
        if params:
            self.irc.part_channel(params)
        else:
            self.irc.say(self.part.__doc__)

    @utils.admin
    def quit(self, params=None):
        """Quit and shut down"""
        self.irc.say("Later!")
        sys.exit(0)
