#   Copyright 2014-2015 Philip Schwartz
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

"""Pyhole Color Unit Tests"""

import re
import unittest

from pyhole.core import color
from pyhole.core import colormap


class MockColors(colormap.ColorMap):
    _attribute = u'\x03'
    _separator = u','
    _digit = u'\x16\x16'
    _reset = u'\x0f'
    _clean = re.compile(r"([\x02\x0F\x1F\x0E\x16\x1B]|\x03([0-9]{0,2})(,([0-9]"
                        "{0,2}))?|\x04[0-9A-Fa-f]{6}(,([0-9A-Fa-f]){6})?)*")
    _color_map = {
        u'red': u'0',
        u'white': u'1',
        u'blue': u'2'
    }

    def color(self, _color):
        _color = _color.lower().strip()
        if _color not in self._color_map:
            raise color.UnknownColor, _color
        return self._color_map[_color]

    def strip(self, text):
        text = self._clean.sub(u'', text)
        text = text.replace(self._reset, u'')
        return text


class TestColor(unittest.TestCase):
    def setUp(self):
        self._colors = color.Color(MockColors)

    def test_colorize(self):
        result = self._colors.colorize("red", "blue", "test")
        self.assertEqual(result, u'\x030,2test\x0f')

    def test_colorize_fg(self):
        result = self._colors.colorize("red", text="test")
        self.assertEqual(result, u'\x030test\x0f')

    def test_colorize_bg(self):
        result = self._colors.colorize(bg="blue", text="test")
        self.assertEqual(result, u'\x03,2test\x0f')

    def test_long_colorize(self):
        enc = self._colors.colorize("red", text="test")
        result = enc + " Nice " + enc
        self.assertEqual(result, u'\x030test\x0f Nice \x030test\x0f')

    def test_clean(self):
        result = self._colors.clean(u'\x030,2test\x0f')
        self.assertEqual(result, u'test')

    def test_long_clean(self):
        result = self._colors.clean(u'\x030test\x0f Nice \x030test\x0f')
        self.assertEqual(result, u'test Nice test')
