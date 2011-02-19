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

"""Intelligent Configuration Library"""

import ConfigParser
import sys


class Config(object):
    """A configuration object"""

    def __init__(self, config, section):
        self.config = ConfigParser.ConfigParser()
        self.section = section

        try:
            conf_file = open(config)
            self.config.readfp(conf_file)
            conf_file.close()
        except IOError:
            sys.exit("No such file: '%s'" % config)

    def sections(self):
        """Return a list of sections"""
        return self.config.sections()

    def get(self, key, param_type="string"):
        """Retrieve configuration values"""
        if param_type == "int":
            return self.config.getint(self.section, key)
        elif param_type == "bool":
            return self.config.getboolean(self.section, key)
        elif param_type == "list":
            return self.config.get(self.section, key).split(", ")
        else:
            return self.config.get(self.section, key)
