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

"""Pyhole Utility Library"""

import eventlet
import logging
import re
import string


eventlet.monkey_patch()


def logger(name, debug=False):
    """Log handler"""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S")
    return logging.getLogger(name)


def admin(func):
    """Administration Decorator"""
    def f(self, *args, **kwargs):
        if self.irc.source in self.irc.admins:
            func(self, *args, **kwargs)
        else:
            self.irc.say("Sorry, you are not authorized to do that.")
    f.__doc__ = func.__doc__
    return f


def spawn(func):
    """Greenthread Spawning Decorator"""
    def f(self, *args, **kwargs):
        eventlet.spawn_n(func, self, *args, **kwargs)
    f.__doc__ = func.__doc__
    return f


def decode_entities(html):
    """Strip HTML entities from a string"""
    html = re.sub("<[^>]*?>", "", html)
    html = re.sub("&nbsp;", " ", html)
    html = re.sub("&amp;", "&", html)
    html = re.sub("&quot;", "\"", html)
    html = re.sub("&#8212;", "-", html)
    html = re.sub("&#8217;", "'", html)
    html = re.sub("&#8220;", "\"", html)
    html = re.sub("&#8221;", "\"", html)
    html = re.sub("&#8230;", "...", html)
    html = filter(lambda x: x in string.printable, html)

    return html.strip()


def ensure_int(param):
    """Ensure the given param is an int"""
    try:
        int(param)
    except ValueError:
        return
