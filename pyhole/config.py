"""Intelligent Configuration Library"""


import ConfigParser
import sys


class Config(object):
    """A configuration object"""

    def __init__(self, file, section):
        self.config = ConfigParser.ConfigParser()
        self.section = section

        try:
            with open(file) as f:
                self.config.readfp(f)
            f.closed
        except IOError:
            sys.exit("No such file: '%s'" % file)

    def sections(self):
        """Return a list of sections"""
        return self.config.sections()

    def get(self, key, type="string"):
        """Retrieve configuration values"""
        if type == "int":
            return self.config.getint(self.section, key)
        elif type == "bool":
            return self.config.getboolean(self.section, key)
        elif type == "list":
            return self.config.get(self.section, key).split(", ")
        else:
            return self.config.get(self.section, key)
