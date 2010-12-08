"""Pyhole Administration"""


import sys


class Admin(object):
    """Provide administration functionality"""

    def __init__(self, irc):
        self.irc = irc

    def help(self, params=None):
        """Learn how to use active modules (ex: .help <topic>)"""
        if params:
            # Temporarily load the class for __doc__ access
            module = params.split(".")[0]
            exec("import %s\n%s = %s.%s(self.irc)" % (
                module,
                module.capitalize(),
                module,
                module.capitalize()))

            doc = eval("%s.__doc__" % params.capitalize())
            self.irc.send_msg(doc)

            # Destroy the class
            exec("%s = None" % module.capitalize())
        else:
            self.irc.send_msg(self.help.__doc__)
            self.irc.send_msg(self.irc.active_commands())

    def reload(self):
        """Reload all modules"""
        self.irc.load_modules(reload_mods=True)
        self.irc.send_msg(self.irc.active_modules())

    def info(self, params=None):
        """Access various statistics (ex: .info <topic>)"""
        if params == "channels":
            self.irc.send_msg(self.irc.active_channels())
        else:
            self.irc.send_msg(self.info.__doc__)

    def join(self, params=None):
        """Join a channel (ex: .join #channel [<key>])"""
        if params:
            self.irc.join_channel(params)
        else:
            self.irc.send_msg(self.join.__doc__)

    def part(self, params=None):
        """Part a channel (ex: .part <channel>)"""
        if params:
            self.irc.part_channel(params)
        else:
            self.irc.send_msg(self.part.__doc__)

    def quit(self):
        """Quit and shutdown"""
        self.irc.connection.quit()
        sys.exit(0)
