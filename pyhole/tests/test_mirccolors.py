#   Copyright 2014 Philip Schwartz
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

"""Pyhole Mirc Colors Unit Tests"""

import unittest

from pyhole.core import color
from pyhole.core.colormaps import mirccolors


class TestMircColors(unittest.TestCase):
    def setUp(self):
        self._colors = color.Color(mirccolors.MircColors)

    def test_colorize(self):
        result = self._colors.colorize("red", "blue", "test")
        self.assertEqual(result, u'\x034,2test\x0f')

    def test_colorize_fg(self):
        result = self._colors.colorize("red", text="test")
        self.assertEqual(result, u'\x034test\x0f')

    def test_colorize_bg(self):
        result = self._colors.colorize(bg="blue", text="test")
        self.assertEqual(result, u'\x03,2test\x0f')

    def test_long_colorize(self):
        enc = self._colors.colorize("red", text="test")
        result = enc + " Nice " + enc
        self.assertEqual(result, u'\x034test\x0f Nice \x034test\x0f')

    def test_clean(self):
        result = self._colors.clean(u'\x030,2test\x0f')
        self.assertEqual(result, u'test')

    def test_long_clean(self):
        result = self._colors.clean(u'\x030test\x0f Nice \x030test\x0f')
        self.assertEqual(result, u'test Nice test')
