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
#

import re

from ..color import UnknownColor
from ..colormap import ColorMap


class MircColors(ColorMap):
    """Mirc Color code schema
        Defined at http://www.mirc.com/colors.html
    """

    _attribute = u'\x03'
    _separator = u','
    _digit = u'\x16\x16'
    _reset = u'\x0f'
    _clean = re.compile(r"([\x02\x0F\x1F\x0E\x16\x1B]|\x03([0-9]{0,2})(,([0-9"
                        "]{0,2}))?|\x04[0-9A-Fa-f]{6}(,([0-9A-Fa-f]){6})?)*")
    _color_map = {
        u'white': u'0',
        u'black': u'1',
        u'blue': u'2',
        u'green': u'3',
        u'red': u'4',
        u'brown': u'5',
        u'purple': u'6',
        u'orange': u'7',
        u'yellow': u'8',
        u'light green': u'9',
        u'teal': u'10',
        u'light cyan': u'11',
        u'light blue': u'12',
        u'pink': u'13',
        u'grey': u'14',
        u'light grey': u'15'
    }

    def color(self, _color):
        _color = _color.lower().strip()
        if _color not in self._color_map:
            raise (UnknownColor, _color)
        return self._color_map[_color]

    def strip(self, text):
        text = self._clean.sub(u'', text)
        text = text.replace(self._reset, u'')
        return text
