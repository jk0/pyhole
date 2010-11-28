""" Pyhole Administration """


import sys


class Admin(object):
    """ Provide administration functionality """

    def __init__(self, irc):
        self.irc = irc

    def reload(self):
        pass

    def join(self):
        pass

    def part(self):
        pass

    def quit(self):
        self.irc.connection.quit()
        sys.exit(0)
