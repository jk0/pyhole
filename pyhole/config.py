""" An intelligent configuration library """


import argparse
import ConfigParser


class Config(object):
    """ A configuration object """

    def __init__(self, file, section):
        self.parser = argparse.ArgumentParser()
        self.args = self.parser.parse_args()

        self.config = ConfigParser.ConfigParser()
        with open(file) as f:
            self.config.readfp(f)
        f.closed
        self.section = section

    def get(self, key, type="string"):
        """ Retrieve configuration values """
        if type == "int":
            return self.config.getint(self.section, key)
        elif type == "bool":
            return self.config.getboolean(self.section, key)
        else:
            return self.config.get(self.section, key)
