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

"""Pyhole Configuration Library"""

from __future__ import with_statement

import ConfigParser
import os
import sys

import utils


class Config(object):
    """A configuration object."""

    def __init__(self, config, section):
        self.config = os.path.abspath(config)
        self.config_parser = ConfigParser.ConfigParser()
        self.section = section

        try:
            with open(self.config) as conf_file:
                self.config_parser.readfp(conf_file)
        except IOError:
            print "Unable to load configuration file: %s" % self.config
            utils.generate_config()
            sys.exit(1)

    def __str__(self):
        """Make the config object readable for logging."""
        return self.section

    def sections(self):
        """Return a list of sections."""
        return self.config_parser.sections()

    def get(self, option, **kwargs):
        """Retrieve configuration values."""
        _type = kwargs.get("type", "str")

        try:
            if _type == "int":
                return self.config_parser.getint(self.section, option)
            elif _type == "bool":
                return self.config_parser.getboolean(self.section, option)
            elif _type == "list":
                return self.config_parser.get(self.section, option).split(", ")
            else:
                return self.config_parser.get(self.section, option)
        except ConfigParser.NoOptionError:
            if "default" in kwargs:
                return kwargs["default"]

            print "Unable to locate '%s' in %s" % (option, self.config)
            print "[%s]" % self.section
            print "%s: value" % option
            sys.exit(1)
