#   Copyright 2011 Josh Kearney
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

"""Pyhole IRC Unit Tests"""

import unittest

from pyhole import irc


class TestIrc(unittest.TestCase):
    def test_active_commands(self):
        active_commands = irc.active_commands()
        self.assertTrue(isinstance(active_commands, str))

    def test_active_keywords(self):
        active_keywords = irc.active_keywords()
        self.assertTrue(isinstance(active_keywords, str))
