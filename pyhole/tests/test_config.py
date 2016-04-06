#   Copyright 2011-2015 Josh Kearney
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

"""Pyhole Config Unit Tests"""

import unittest

from pyhole.core import config
from pyhole.core import utils


class TestConfig(unittest.TestCase):
    def setUp(self):
        home_dir = utils.get_home_directory()
        self.config = config.Config(home_dir + "pyhole.conf", "Pyhole")

    def test_missing_parameter(self):
        self.assertRaises(SystemExit, self.config.get, "foo")

    def test_sections(self):
        sections = self.config.sections()
        self.assertTrue(isinstance(sections, list))
        self.assertTrue(len(sections) > 1)

    def test_get_int(self):
        test_int = self.config.get("reconnect_delay", type="int")
        self.assertTrue(isinstance(test_int, int))

    def test_get_bool(self):
        test_bool = self.config.get("debug", type="bool")
        self.assertTrue(isinstance(test_bool, bool))

    def test_get_list(self):
        test_list = self.config.get("admins", type="list")
        self.assertTrue(isinstance(test_list, list))

    def test_get_str(self):
        test_str = self.config.get("command_prefix")
        self.assertTrue(isinstance(test_str, str))
