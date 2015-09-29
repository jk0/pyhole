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


class UnknownColor(Exception):
    """Raised when an unknown color is requested"""


class Color(object):
    """API for accessing colorization in a generic manner"""

    def __init__(self, _colors=None):
        if not _colors:
            from colormaps.mirccolors import MircColors
            _colors = MircColors
        self._colors = _colors()

    def colorize(self, fg=None, bg=None, text=None):
        """Generate colored text using passed parameters"""
        if not fg and not bg:
            return self._colors._reset
        if fg:
            fg = self._colors.color(fg)
        if bg:
            bg = self._colors.color(bg)
        codes = []
        if fg is None:
            codes.append(u'')
        else:
            codes.append(fg)
        if bg is not None:
            codes.append(bg)
        color = self._colors._attribute + self._colors._separator.join(codes)
        if text is not None and text[0].isdigit():
            color += self._colors._digit
        if text is not None:
            return u'%s%s%s' % (color, text, self._colors._reset)
        else:
            return color

    # added with the api into the ColorMap to strip color codes if needed.
    def clean(self, text):
        """Strip color codes from passed string."""
        return self._colors.strip(text)
