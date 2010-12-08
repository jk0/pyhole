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
            self.irc.send_msg(", ".join(self.irc.commands))

    def reload(self):
        """Reload all modules"""
        self.irc.load_modules()
        self.irc.send_msg("Loaded Modules: %s" % ", ".join(self.irc.modules))

    def join(self, params):
        """Join a channel"""
        pass

    def part(self, params):
        """Part a channel"""
        pass

    def quit(self):
        """Quit and shutdown"""
        self.irc.connection.quit()
        sys.exit(0)
